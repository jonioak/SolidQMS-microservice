from fastapi import APIRouter

router = APIRouter(prefix="/api/v1", tags=["Sample"])

@router.get("/sample")
async def get_sample_text():
    return {"sample_text": "This is a sample text response from SolidQMS AI Microservice."}
