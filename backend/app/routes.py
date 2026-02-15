from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
def health_check():
    return {"status": "healthy"}

@router.get("/api/message")
def get_message():
    return {"message": "Hello from FastAPI backend"}
