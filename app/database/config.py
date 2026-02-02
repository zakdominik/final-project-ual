from dotenv import load_dotenv
import os

#loads env file
load_dotenv()

#database connection information
DATABASE_URL = os.getenv("DATABASE_URL")

#gets api keys
OPENAI_API_KEY = os.getenv("OPENAI_KEY")
NEWSDATA_API_KEY = os.getenv("NEWSDATA_KEY")