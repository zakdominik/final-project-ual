import json
from openai import OpenAI
from app.database.config import OPENAI_API_KEY

#initialises the client
client = OpenAI(api_key=OPENAI_API_KEY)

#analyses an article to identify the party it is mainly about and gives sentiment rating
def analyze_article_sentiment(headline: str, snippet: str):
    #refined prompt
    system_msg = (
        "You are a political data analyst. Analyze the UK news headline and snippet. "
        "1. Identify the primary party the article influences (Options: 'Labour', 'Conservatives', 'Reform'). "
        "If none or multiple equally, choose 'Other'. "
        "2. Provide a sentiment score from -1.0 (very negative/critical) to +1.0 (very positive/supportive). "
        "3. Output strictly in JSON format: {\"party\": \"Name\", \"sentiment\": 0.0}"
    )
    #input to be classified
    user_msg = f"Headline: {headline}\nSnippet: {snippet}"

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_msg}
            ],
            temperature=0,  #deterministic result
            response_format={"type": "json_object"}  #forces json format
        )

        #parses json openai format
        result_text = response.choices[0].message.content
        data = json.loads(result_text)
        #returns dictionary in the format i want
        return {
            "party": data.get("party", "Other"),
            "sentiment": float(data.get("sentiment", 0.0))
        }
    except Exception as e:
        print(f"The model failed: {e}")
        #neutral return if it fails
        return {"party": "Other", "sentiment": 0.0}