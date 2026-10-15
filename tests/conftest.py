import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app

# Database configuratie
from app.db.database import Base, get_db
from app.utils.security import verify_api_key

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

    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        yield db  # Hier pauzeert de fixture en geeft hij de 'db' aan jouw test
    finally:
        db.close()
        # Ruim de rommel op na de test
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db_session):
    """
    Tijdens de tests NIET de echte database gebruiken, maar de test-database hierboven.
    De TestClient stuurt automatisch de test API-key mee als header,
    zodat de globale verify_api_key dependency niet blokkeert.
    """
    def override_get_db():
        yield db_session

    def override_verify_api_key():
        """Sla de API-key check over in tests — security wordt apart getest in test_security.py."""
        return "test_sleutel"

    # 'Override' de originele dependencies met test versies
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[verify_api_key] = override_verify_api_key

    with TestClient(app) as test_client:
        yield test_client

    # Ruim de overrides op na de test
    app.dependency_overrides.clear()