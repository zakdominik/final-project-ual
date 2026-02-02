from app.database.database import engine, Base


#deletes all tables
print("Dropping all tables...")
Base.metadata.drop_all(bind=engine)
#creates tables again
print("Creating new tables")
Base.metadata.create_all(bind=engine)

print("Database reset complete")