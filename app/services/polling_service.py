import requests
import json
import pandas as pd


#gets the latest UK polling data from wikipedia
def fetch_polling_data():
    print("Connecting to Wikipedia API for polling data")

    #disclaimer: AI helped me in getting the proper parameters etc.
    #Wiki API endpoint
    url = "https://commons.wikimedia.org/w/api.php"
    #parameters to access the content
    params = {
        "action": "query",
        "format": "json",
        "titles": "Data:Opinion_polling_for_the_next_United_Kingdom_general_election_(post-2024).tab",
        "prop": "revisions",
        "rvprop": "content",
        "rvslots": "main",
        "origin": "*"
    }
    #identification of myself to the api
    headers = {
        "User-Agent": "UniversityProject/1.0"
    }

    try:
        response = requests.get(url, params=params, headers=headers)
        data = response.json()
        #gets actual data
        pages = data['query']['pages']
        #gets the first key
        page_id = list(pages.keys())[0]

        #extarcts string content
        raw_json_string = pages[page_id]['revisions'][0]['slots']['main']['*']
        parsed_content = json.loads(raw_json_string)

        column_names = [field['name'] for field in parsed_content['schema']['fields']]
        poll_data = parsed_content['data']

        df = pd.DataFrame(poll_data, columns=column_names)

        #clean and rename columns
        df = df.rename(columns={
            'polldate': 'Date',
            'LAB': 'Labour',
            'CON': 'Conservatives',
            'RFM': 'Reform'
        })

        if 'Pollster' not in df.columns:
            df['Pollster'] = 'Unknown'

        #keep only the columns that are needed
        df = df[['Date', 'Pollster', 'Labour', 'Conservatives', 'Reform']]
        #fixes date format
        df['Date'] = pd.to_datetime(df['Date'])
        #newest first
        df = df.sort_values(by='Date', ascending=False)
        #fills empty cells with 0 to avoid errors
        df = df.fillna(0.0)
        recent_polls = df.head(20).to_dict(orient='records')
        print(f"Successfully loaded {len(recent_polls)} recent polls")
        return recent_polls

    except Exception as e:
        print(f"Error fetching Wikipedia data: {e}")
        return []