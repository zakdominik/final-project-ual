import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

#get url
DATABASE_URL = os.getenv("DATABASE_URL")
#fixes postgres issue for heroku
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
#establish db engine
if "sqlite" in DATABASE_URL:
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

#used for connecting to the db
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()