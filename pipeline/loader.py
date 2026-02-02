from sqlalchemy.orm import Session
from app.models.sql_models import Article, ArticleEvaluated, Party, Source, Poll

#helper function which helps find database ID based on party name
def get_party_id(db: Session, party_name):
    #manual cleaning
    if party_name in ["Tories", "Conservative Party"]:
        party_name = "Conservatives"
    #query
    party = db.query(Party).filter(Party.party_name == party_name).first()

    #if id found, return it, otherwise none
    if party:
        return party.id
    else:
        return None

#saves a news article to the db
def load_article(db: Session, data):
    #checks for duplicates based on url
    existing_article = db.query(Article).filter(Article.url == data['url']).first()
    if existing_article:
        return None

    #source handling
    source = db.query(Source).filter(Source.source_name == data['source_id']).first()
    if not source:
        #if new source, add to db
        source = Source(source_name=data['source_id'])
        db.add(source)
        db.commit()

    #creates a new article record
    new_article = Article(
        title=data['title'],
        description=data['description'],
        url=data['url'],
        date=data['date'],
        source_id=source.id
    )
    #save to db
    db.add(new_article)
    db.commit()
    db.refresh(new_article)

    return new_article


def load_evaluation(db: Session, article_id, ai_result):
    """
    Saves the sentiment score (AI result) for a specific article and party.
    """
    # Use our helper to get the correct Party ID
    party_id = get_party_id(db, ai_result['party'])

    if party_id:
        # Create the evaluation record
        evaluation = ArticleEvaluated(
            article_id=article_id,
            party_id=party_id,
            sentiment_score=ai_result['sentiment']
        )
        db.add(evaluation)
        db.commit()
        # Optional: Print to console so we can see it working
        print(f"   [LOADER] Saved score for {ai_result['party']}: {ai_result['sentiment']}")

#saves a single polling datapoint
def load_poll(db: Session, poll_data):
    party_id = get_party_id(db, poll_data['party_name'])

    #if dont recognize party_id, skip it
    if not party_id:
        return

    #duplicate check
    exists = db.query(Poll).filter(Poll.date == poll_data['date'],Poll.party_id == party_id,Poll.pollster_name == poll_data['pollster']).first()
    if exists:
        return

    #add the new pol
    new_poll = Poll(
        party_id=party_id,
        rating=poll_data['rating'],
        date=poll_data['date'],
        pollster_name=poll_data['pollster']
    )
    db.add(new_poll)
    db.commit()
    print(f"Loader. saved poll: {poll_data['party_name']} ({poll_data['rating']}%)")

#converts rows from old format to individual rows to make it relational
def load_polls_batch(db: Session, clean_polls):
    for poll_row in clean_polls:
        parties_to_save = ["Labour", "Conservatives", "Reform"]
        for party in parties_to_save:
            #check if exists
            if party in poll_row:
                #reshape the data
                single_poll_entry = {
                    'date': poll_row['date'],
                    'pollster': poll_row['pollster'],
                    'party_name': party,
                    'rating': poll_row[party]
                }
                #call the previous function to load the single point
                load_poll(db, single_poll_entry)