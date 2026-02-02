from newsdataapi import NewsDataApiClient
from app.database.config import NEWSDATA_API_KEY

#initialises api client
api = NewsDataApiClient(apikey=NEWSDATA_API_KEY)

#fetches 50 latest articles and returns a list of dictionaries which is formatted for the db
def fetch_daily_news():
    #domains used for the project
    domain_list = "bbc,theguardiantheguardian,skynews,independentuk,dailymailuk"

    print("Fetching daily news from API source:")

    try:
        response_generator = api.latest_api(
            q='Labour OR Starmer OR Tories OR Conservatives OR "Conservative Party" OR Reform OR Farage OR Badenoch',
            domain=domain_list,
            country="gb",
            category="politics",
            language="en",
            paginate=True,
            max_pages=1  #5 pages with 10 articles each
        )

        cleaned_articles = []

        #as it is requesting multiple pages, it needs to loop over them
        for page_data in response_generator:
            if page_data.get('status') != 'success': #checks for errors
                print("NewsData API Page Error.")
                continue
            #stores results
            results = page_data.get('results', [])

            for item in results:
                #checks for duplicates and missing data
                if not item.get('title') or not item.get('link'):
                    continue
                #formats the output
                cleaned_articles.append({
                    'source_id': item.get('source_id'),
                    'title': item.get('title'),
                    'description': item.get('description', ''),
                    'url': item.get('link'),
                    'date': item.get('pubDate')
                })
        print(f"Successfully got {len(cleaned_articles)} articles")
        return cleaned_articles

    except Exception as e:
        print(f"News fetch error: {e}")
        return []