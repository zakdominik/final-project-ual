from app.database.database import SessionLocal
import extractor, transformer, loader, analysis


def run_pipeline():
    db = SessionLocal()
    print("ETL start")

    #extract: news
    raw_articles = extractor.extract_news()

    for item in raw_articles:
        #transform: clean data
        clean_data = transformer.transform_news_item(item)
        #load article
        article_obj = loader.load_article(db, clean_data)

        #if new: enrich it with party classification and sentiment score
        if article_obj:
            #transform: openai model
            ai_scores = transformer.enrich_with_ai(clean_data)
            #load: save scores into db
            if ai_scores:
                for party_name, score in ai_scores.items():
                    eval_data = {'party': party_name,'sentiment': score}
                    loader.load_evaluation(db, article_obj.id, eval_data)

    #extract: poll data
    raw_polls = extractor.extract_polls()
    if raw_polls:
        #transform: cleans the data
        clean_polls = transformer.transform_polls(raw_polls)
        #load: saves the batch of data into the db
        loader.load_polls_batch(db, clean_polls)

    #runs the statistical analysis
    analysis.run_daily_analysis()

    print("Pipeline end")
    db.close()


if __name__ == "__main__":
    run_pipeline()