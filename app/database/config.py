import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_KEY") # Make sure Heroku var name matches this string ("OPENAI_KEY")
NEWSDATA_API_KEY = os.getenv("NEWSDATA_KEY") # Make sure Heroku var name matches this string ("NEWSDATA_KEY")
