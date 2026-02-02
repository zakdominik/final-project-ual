import sys
import os
from app.database.database import engine, Base
from app.models.sql_models import Party, Source, Article, ArticleEvaluated, Poll, DailyData, Result

#adds the project root to the path so python can find app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

#used for initialising tables in the db
def init_db():
    print("Creating database tables")
    try:
        #generates crate table queries for all table models
        Base.metadata.create_all(bind=engine)
        print("Tables created successfully")
    except Exception as e:
        print(f"Error creating database: {e}")

if __name__ == "__main__":
    init_db()