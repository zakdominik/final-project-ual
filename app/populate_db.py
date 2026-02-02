from app.database.database import SessionLocal
from app.models.sql_models import Party, Source

#used for populating party and sources tables which are necessary for the etl pipeline
def populate_data():
    db = SessionLocal()

    #party list
    parties = ["Labour", "Conservatives", "Reform"]
    print("Populating parties")
    for name in parties:
        if not db.query(Party).filter(Party.party_name == name).first():
            db.add(Party(party_name=name))
            print(f"Added: {name}")


    #sources in this project
    sources = ["bbc", "theguardiantheguardian", "skynews", "independentuk", "dailymailuk"]
    print("\n Populating sources")
    for source_id in sources:
        if not db.query(Source).filter(Source.source_name == source_id).first():
            db.add(Source(source_name=source_id))
            print(f"Added: {source_id}")

    db.commit()
    db.close()
    print("\n Tables populated")

if __name__ == "__main__":
    populate_data()