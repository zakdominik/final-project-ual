from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from .config import DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME

#puts together the database url for connecting
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
#establishes the db
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

#used for db connections
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()