from dotenv import load_dotenv
import os

#loads env file
load_dotenv()

#database connection information
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

#gets api keys
OPENAI_API_KEY = os.getenv("OPENAI_KEY")
NEWSDATA_API_KEY = os.getenv("NEWSDATA_KEY")