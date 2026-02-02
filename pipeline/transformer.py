from app.services.openai_service import analyze_article_sentiment
import pandas as pd

#prepares a single news article for the database. combines title and description for more context for GPT model
def transform_news_item(raw_item):
    #extracts title and descriptions
    title = raw_item.get('title', '')
    desc = raw_item.get('description', '')
    #safety check
    if desc is None:
        desc = ""

   #combined text, used for the model later
    full_text = f"{title}. {desc}"
    #creates clean, formatted dict
    formatted_item = {
        'source_id': raw_item.get('source_id'),
        'title': title,
        'description': desc,
        'url': raw_item.get('url'),
        'date': raw_item.get('date'),
        'full_text': full_text
    }
    #returns dict
    return formatted_item

#calls for openai model to get sentiment scores+party
def enrich_with_ai(clean_item):
    #uses the helper function created before
    sentiment_scores = analyze_article_sentiment(clean_item['title'],clean_item['description'])
    return sentiment_scores

#cleans up polling data, make sure all party names etc. match throughout the db
def transform_polls(raw_polls):
    #if returns nothing, stops here
    if not raw_polls:
        return []

    clean_polls = []
    #loops through every row of data
    for row in raw_polls:
        #fixes date
        poll_date = row.get('Date')
        # pd.notna checks if the date is valid
        if pd.notna(poll_date):
            poll_date = str(poll_date).split(" ")[0]
        #creates clean poll entry, manually maps the columns
        poll_entry = {
            "date": poll_date,
            "pollster": row.get('Pollster', 'Unknown'),
            "Labour": row.get('Labour', 0),
            "Conservatives": row.get('Conservatives', 0),
            "Reform": row.get('Reform', 0)
        }
        #adds clean row to clean list
        clean_polls.append(poll_entry)

    return clean_polls