import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()

SQLALCHEMY_DATABASE_URL = os.getenv(

    "DATABASE_URL", 
    "postgresql://admin:secretpassword@127.0.0.1:5433/solidqms_ai"
)

# De SQLAlchemy motor
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# De sessie-fabriek
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# De fundering voor de modellen
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()