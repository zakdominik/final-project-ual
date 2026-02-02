from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from pydantic import BaseModel
from app.database.database import get_db
from app.models.sql_models import Party, DailyData, Result, Poll, Source, Article, ArticleEvaluated

router = APIRouter()


#definition of schemas
class PartyResponse(BaseModel):
    id: int
    name: str

class SourceResponse(BaseModel):
    id: int
    name: str

class TrendPoint(BaseModel):
    date: date
    sentiment: Optional[float]
    poll_rating: Optional[float]

class CorrelationResponse(BaseModel):
    party: str
    correlation: float
    p_value: Optional[float]
    last_updated: date
    status: str

class PollResponse(BaseModel):
    date: date
    rating: float
    pollster: str

class ArticleResponse(BaseModel):
    id: int
    title: Optional[str]
    url: Optional[str]
    date: Optional[date]
    source: str


#helper function, defines correlation status for the api
def get_correlation_status(corr_value):
    if corr_value is None:
        return "Insufficient Data"
    if corr_value > 0.5:
        return "Strong Positive"
    if corr_value > 0.1:
        return "Weak Positive"
    if corr_value < -0.5:
        return "Strong Negative"
    if corr_value < -0.1:
        return "Weak Negative"
    return "Neutral"


#API endpoints

#gets the list of all political parties in the db
@router.get("/parties", response_model=List[PartyResponse])
def get_parties(db: Session = Depends(get_db)):
    all_parties = db.query(Party).all()
    #converts the db data into valid format
    response_list = []
    for p in all_parties:
        response_list.append({"id": p.id, "name": p.party_name})
    return response_list


#gets a list of all news sources used in the project
@router.get("/sources", response_model=List[SourceResponse])
def get_sources(db: Session = Depends(get_db)):
    all_sources = db.query(Source).all()
    #converts into valid format
    response_list = []
    for s in all_sources:
        response_list.append({"id": s.id, "name": s.source_name})
    return response_list


#gets the correlation for every party
@router.get("/results", response_model=List[CorrelationResponse])
def get_results(db: Session = Depends(get_db)):
    parties = db.query(Party).all()
    results_list = []
    #gets the most recent result
    for party in parties:
        latest_entry = (
            db.query(Result)
            .join(DailyData)
            .filter(DailyData.party_id == party.id)
            .order_by(DailyData.date.desc())
            .first()
        )
        #formatting
        if latest_entry:
            results_list.append({
                "party": party.party_name,
                "correlation": latest_entry.correlation_coefficient,
                "p_value": latest_entry.p_value,
                "last_updated": latest_entry.daily_data.date,
                "status": get_correlation_status(latest_entry.correlation_coefficient)
            })
    return results_list


#gets the result for a specific party
@router.get("/results/{party_id}", response_model=CorrelationResponse)
def get_party_result(party_id: int, db: Session = Depends(get_db)):
    #cheks if party exists
    party = db.query(Party).filter(Party.id == party_id).first()
    if not party:
        raise HTTPException(status_code=404, detail="Party not found")
    #latest result
    latest_entry = (
        db.query(Result)
        .join(DailyData)
        .filter(DailyData.party_id == party_id)
        .order_by(DailyData.date.desc())
        .first()
    )
    #if no results:
    if not latest_entry:
        raise HTTPException(status_code=404, detail="No analysis results found for this party yet")
    #formats the return
    return {
        "party": party.party_name,
        "correlation": latest_entry.correlation_coefficient,
        "p_value": latest_entry.p_value,
        "last_updated": latest_entry.daily_data.date,
        "status": get_correlation_status(latest_entry.correlation_coefficient)
    }


#gets daily sentiment and poll data for a party (for ex. for graphing purposes)
@router.get("/trends/{party_id}", response_model=List[TrendPoint])
def get_trends(party_id: int, db: Session = Depends(get_db)):

    #gets all data for the party
    data = db.query(DailyData).filter(DailyData.party_id == party_id).order_by(DailyData.date.asc()).all()
    if not data:
        return []
    #formats the data
    trend_list = []
    for d in data:
        trend_list.append({
            "date": d.date,
            "sentiment": d.sentiment_avg,
            "poll_rating": d.interpolated_poll_rating
        })
    return trend_list


#gets polling data for a specific party
@router.get("/polls/{party_id}", response_model=List[PollResponse])
def get_polls(party_id: int, db: Session = Depends(get_db)):
    polls = db.query(Poll).filter(Poll.party_id == party_id).order_by(Poll.date.desc()).all()
    if not polls:
        return []

    response_list = []
    for p in polls:
        response_list.append({
            "date": p.date,
            "rating": p.rating,
            "pollster": p.pollster_name
        })
    return response_list


#gets a specific article by its id
@router.get("/articles/{article_id}", response_model=ArticleResponse)
def get_article(article_id: int, db: Session = Depends(get_db)):

    article = db.query(Article).filter(Article.id == article_id).first()

    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    return {
        "id": article.id,
        "title": article.title,
        "url": article.url,
        "date": article.date,
        #checks if source exists to avoid errors
        "source": article.source.source_name if article.source else "Unknown"
    }


#gets all articles related to a specific party
@router.get("/articles/party/{party_id}", response_model=List[ArticleResponse])
def get_party_articles(party_id: int, db: Session = Depends(get_db)):
    # find all evaluated articles
    evaluations = db.query(ArticleEvaluated).filter(ArticleEvaluated.party_id == party_id).all()
    if not evaluations:
        return []

    articles_list = []
    for eva in evaluations:
        art = eva.article
        articles_list.append({
            "id": art.id,
            "title": art.title,
            "url": art.url,
            "date": art.date,
            "source": art.source.source_name if art.source else "Unknown"
        })
    return articles_list