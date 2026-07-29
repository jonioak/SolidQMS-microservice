from fastapi import FastAPI
from app.controllers.generation import router as generation_router
from app.controllers.prompts import router as prompts_router
from app.controllers.sample import router as sample_router

app = FastAPI(
    title="SolidQMS AI Microservice",
    description="Asynchrone AI Microservice voor 8D Kwaliteitsmanagement generatie en ondersteuning",
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