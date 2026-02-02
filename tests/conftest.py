import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.database.database import Base, get_db
from app.main import app

#in memory db for testing
TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


#connects to fake memory db
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()
#applies the override
app.dependency_overrides[get_db] = override_get_db

#creates a new fresh db for every test function
@pytest.fixture(scope="function")
def client():
    #creates the tables
    Base.metadata.create_all(bind=engine)
    #returns test client
    with TestClient(app) as c:
        yield c
    #drop tables when done
    Base.metadata.drop_all(bind=engine)

#gives test access to the db
@pytest.fixture(scope="function")
def db_session():
    session = TestingSessionLocal()
    yield session
    session.close()