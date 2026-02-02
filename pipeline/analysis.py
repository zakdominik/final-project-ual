import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
from app.database.database import SessionLocal
from app.models.sql_models import Article, ArticleEvaluated, Poll, Party, DailyData, Result
from datetime import timedelta

#gets raw data from sql and converts to pd df. easier for the analysis
def get_data_as_dataframe(db: Session):

    #fetch sentiment data (joined with articles to get the date)
    #needed: date, party, score
    sentiment_query = db.query(Article.date,ArticleEvaluated.party_id,ArticleEvaluated.sentiment_score).join(ArticleEvaluated, Article.id == ArticleEvaluated.article_id).all()
    if not sentiment_query:
        print("Analysis: no sentiment data found.")
        return None, None

    #convert to df
    df_sentiment = pd.DataFrame(sentiment_query, columns=['date', 'party_id', 'score'])
    #columns datatype check
    df_sentiment['date'] = pd.to_datetime(df_sentiment['date'])

    #get all polling data
    polls_query = db.query(Poll.date, Poll.party_id, Poll.rating).all()
    df_polls = pd.DataFrame(polls_query, columns=['date', 'party_id', 'rating'])
    if not df_polls.empty:
        df_polls['date'] = pd.to_datetime(df_polls['date'])
    return df_sentiment, df_polls

#this is the main function that calculates daily avgs and correlations
def run_daily_analysis():
    db = SessionLocal()
    print("Starting analysis")

    #gets data
    df_sentiment, df_polls = get_data_as_dataframe(db)
    #checks if it contains sentiment data
    if df_sentiment is None:
        db.close()
        return

    #loops through parties and analyses each individually
    all_parties = db.query(Party).all()
    for party in all_parties:
        if party.party_name not in ["Labour", "Conservatives", "Reform"]:
            continue
        print(f"Analyzing Party: {party.party_name}")
        #filter data for party
        party_sent = df_sentiment[df_sentiment['party_id'] == party.id]
        if party_sent.empty:
            continue
        #calculate daily sentiment avg
        daily_sent = party_sent.groupby('date')['score'].mean().reset_index()
        daily_sent.set_index('date', inplace=True)

        #prepare polling data for interpolation because polls aren't released daily
        if not df_polls.empty:
            party_polls = df_polls[df_polls['party_id'] == party.id].sort_values('date')
            #remove duplicates
            party_polls = party_polls.drop_duplicates(subset=['date'], keep='first')
            party_polls.set_index('date', inplace=True)
            #join on date
            combined_df = daily_sent.join(party_polls, how='outer', lsuffix='_sent', rsuffix='_poll')

            #fills in the missing poll numbers between dates, draws a straight line between two poll dates
            combined_df['interpolated_poll'] = combined_df['rating'].interpolate(method='time')
        else:
            #fallback if no polls exist
            combined_df = daily_sent
            combined_df['interpolated_poll'] = None
        #save results to db, iterates through every day
        for date_idx, row in combined_df.iterrows():
            sql_date = date_idx.date()

            #clean the values
            avg_score = row.get('score')
            if pd.isna(avg_score):
                avg_score = None
            else:
                avg_score = float(avg_score)
            poll_rating = row.get('interpolated_poll')
            if pd.isna(poll_rating):
                poll_rating = None
            else:
                poll_rating = float(poll_rating)

            #check if specific day is already analysed
            exists = db.query(DailyData).filter(DailyData.date == sql_date,DailyData.party_id == party.id).first()

            #if not, add it to db
            if not exists:
                daily_entry = DailyData(
                    date=sql_date,
                    party_id=party.id,
                    sentiment_avg=avg_score,
                    interpolated_poll_rating=poll_rating
                )
                db.add(daily_entry)
                db.commit()
                db.refresh(daily_entry)

                #calculate correlation, only if both polls and scores are available
                if poll_rating is not None and avg_score is not None:
                    #30 day rolling window
                    start_date = date_idx - timedelta(days=30)
                    window_data = combined_df.loc[start_date:date_idx]
                    #at least 5 datapoints needed for the calculation
                    if len(window_data) > 5:
                        #calculates pearson corr
                        corr = window_data['score'].corr(window_data['interpolated_poll'])

                        if not np.isnan(corr):
                            #save the result
                            db.add(Result(
                                daily_data_id=daily_entry.id,
                                correlation_coefficient=float(corr)
                            ))
                            db.commit()
    print("Analysis completed")
    db.close()


if __name__ == "__main__":
    run_daily_analysis()