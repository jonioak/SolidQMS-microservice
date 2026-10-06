import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app

# Database configuratie
from app.db.database import Base, get_db 

# SQLite database voor tests
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    """
    Maakt een verse database aan voor élke individuele test, 
    en gooit deze daarna weer weg (100% isolatie).
    """

    Base.metadata.create_all(bind=engine)
    
    db = TestingSessionLocal()
    try:
        yield db  # Hier pauzeert de fixture en geeft hij de 'db' aan jouw test (TC-03)
    finally:
        db.close()
        # Ruim de rommel op na de test
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db_session):
    """
    Dit is een cruciale stap in FastAPI! 
    We vertellen de API dat hij tijdens de tests NIET de echte database 
    moet gebruiken, maar de test-database die we hierboven hebben gemaakt.
    """
    def override_get_db():
        yield db_session
        
    # 'Override' de originele database dependency met onze test versie
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client