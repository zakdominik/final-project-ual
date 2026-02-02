from sqlalchemy import Column, Integer, String, Float, DateTime, Date, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database.database import Base

#contains all tables used in the db

#defines the table of sources from which there are artciles
class Source(Base):
    __tablename__ = "sources"
    id = Column(Integer, primary_key=True, index=True)
    source_name = Column(String, nullable=False)
    #one source has many articles
    articles = relationship("Article", back_populates="source")

#table of all parties (in this project's case 3)
class Party(Base):
    __tablename__ = "parties"
    id = Column(Integer, primary_key=True, index=True)
    party_name = Column(String, nullable=False)
    #relationships
    evaluations = relationship("ArticleEvaluated", back_populates="party")
    polls = relationship("Poll", back_populates="party")
    daily_data = relationship("DailyData", back_populates="party")

#sets the table for all unevaluated artciles
class Article(Base):
    __tablename__ = "articles"
    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("sources.id"))
    title = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    url = Column(Text, nullable=True)
    date = Column(DateTime, nullable=True)
    #relationships
    source = relationship("Source", back_populates="articles")
    evaluations = relationship("ArticleEvaluated", back_populates="article")

#table for all evaluated articles
class ArticleEvaluated(Base):
    __tablename__ = "articles_evaluated"
    article_id = Column(Integer, ForeignKey("articles.id"), primary_key=True)
    party_id = Column(Integer, ForeignKey("parties.id"), primary_key=True)
    sentiment_score = Column(Float, nullable=True)
    #relationships
    article = relationship("Article", back_populates="evaluations")
    party = relationship("Party", back_populates="evaluations")


#stores polling data from wikipedia
class Poll(Base):
    __tablename__ = "polls"
    id = Column(Integer, primary_key=True, index=True)
    party_id = Column(Integer, ForeignKey("parties.id"))
    rating = Column(Float, nullable=True)
    date = Column(Date, nullable=False)
    pollster_name = Column(String, nullable=True)
    #relationship
    party = relationship("Party", back_populates="polls")

#stores daily information regarding sentiment averages and interpolated polling
class DailyData(Base):
    __tablename__ = "daily_data"
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    party_id = Column(Integer, ForeignKey("parties.id"))
    sentiment_avg = Column(Float, nullable=True)
    interpolated_poll_rating = Column(Float, nullable=True)
    #relationships
    party = relationship("Party", back_populates="daily_data")
    results = relationship("Result", back_populates="daily_data")

#stores results from analysis
class Result(Base):
    __tablename__ = "results"
    id = Column(Integer, primary_key=True, index=True)
    daily_data_id = Column(Integer, ForeignKey("daily_data.id"))
    correlation_coefficient = Column(Float, nullable=True)
    p_value = Column(Float, nullable=True)
    #relationship
    daily_data = relationship("DailyData", back_populates="results")