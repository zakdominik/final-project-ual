from app.models.sql_models import Party, DailyData, Source, Poll, Article, ArticleEvaluated, Result
from datetime import date


#tests parties
def test_get_parties(client, db_session):
    new_party = Party(party_name="Labour")
    db_session.add(new_party)
    db_session.commit()
    response = client.get("/api/v1/parties")
    assert response.status_code == 200
    assert response.json()[0]["name"] == "Labour"


#tests trends
def test_get_trends(client, db_session):
    p = Party(party_name="Tories")
    db_session.add(p)
    db_session.commit()
    d = DailyData(date=date(2024, 1, 1), party_id=p.id, sentiment_avg=0.5, interpolated_poll_rating=30.0)
    db_session.add(d)
    db_session.commit()
    response = client.get(f"/api/v1/trends/{p.id}")
    assert response.status_code == 200
    assert response.json()[0]["poll_rating"] == 30.0


#tests sources
def test_get_sources(client, db_session):
    s = Source(source_name="BBC")
    db_session.add(s)
    db_session.commit()

    response = client.get("/api/v1/sources")
    assert response.status_code == 200
    assert response.json()[0]["name"] == "BBC"


#tests polls
def test_get_polls(client, db_session):
    p = Party(party_name="Reform")
    db_session.add(p)
    db_session.commit()
    poll = Poll(party_id=p.id, rating=15.0, date=date(2024, 1, 1), pollster_name="YouGov")
    db_session.add(poll)
    db_session.commit()
    response = client.get(f"/api/v1/polls/{p.id}")
    assert response.status_code == 200
    assert response.json()[0]["pollster"] == "YouGov"


#tests articles
def test_get_article(client, db_session):
    s = Source(source_name="Skynews")
    db_session.add(s)
    db_session.commit()
    article = Article(title="Test News", url="http://test.com", date=date(2024, 1, 1), source_id=s.id)
    db_session.add(article)
    db_session.commit()
    response = client.get(f"/api/v1/articles/{article.id}")
    assert response.status_code == 200
    assert response.json()["title"] == "Test News"
    response = client.get("/api/v1/articles/999")
    assert response.status_code == 404


#tests articles of a party
def test_get_party_articles(client, db_session):
    p = Party(party_name="Labour")
    s = Source(source_name="BBC")
    db_session.add_all([p, s])
    db_session.commit()
    art = Article(title="Labour Wins", url="http://bbc.co.uk", date=date(2024, 1, 1), source_id=s.id)
    db_session.add(art)
    db_session.commit()
    eva = ArticleEvaluated(article_id=art.id, party_id=p.id, sentiment_score=0.8)
    db_session.add(eva)
    db_session.commit()
    response = client.get(f"/api/v1/articles/party/{p.id}")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["title"] == "Labour Wins"


#tests analysis results
def test_get_results(client, db_session):
    p = Party(party_name="Greens")
    db_session.add(p)
    db_session.commit()
    dd = DailyData(date=date(2024, 1, 1), party_id=p.id)
    db_session.add(dd)
    db_session.commit()
    result = Result(daily_data_id=dd.id, correlation_coefficient=0.9, p_value=0.01)
    db_session.add(result)
    db_session.commit()
    response = client.get("/api/v1/results")
    assert response.status_code == 200
    assert response.json()[0]["correlation"] == 0.9
    response = client.get(f"/api/v1/results/{p.id}")
    assert response.status_code == 200
    assert response.json()["status"] == "Strong Positive"