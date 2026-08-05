import traceback
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.controllers.generation import router as generation_router
from app.controllers.prompts import router as prompts_router
from app.controllers.sample import router as sample_router

from app.db.database import SessionLocal, engine, Base
from app.db.seed import seed_standaard_prompts

# Maak database tabellen aan en voer seeder uit
try:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_standaard_prompts(db)
    finally:
        db.close()
except Exception as e:
    print(f"Kon niet verbinden met de database op startup (Fallback naar in-memory catalogus): {e}")

app = FastAPI(
    title="SolidQMS AI Microservice",
    description="Asynchrone AI Microservice voor 8D Kwaliteitsmanagement generatie en prompt aanpassingen",
    version="1.0.0"
)

# Registreer de API routers
app.include_router(generation_router)
app.include_router(prompts_router)
app.include_router(sample_router)

@app.get("/")
def read_root():
    return {"status": "online", "system": "SolidQMS AI Microservice"}

@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "service": "SolidQMS AI Microservice",
        "version": "1.0.0"
    }