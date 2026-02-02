from app.services.news_service import fetch_daily_news
from app.services.polling_service import fetch_polling_data

#extracts news articles from news api
def extract_news():
    print("Extractor: fetching latest articles")
    #uses the helper file news_service
    return fetch_daily_news()

#extracts poll data from wiki api
def extract_polls():
    print("Extractor: fetching latest polling")
    #uses the helper file polling_service
    return fetch_polling_data()