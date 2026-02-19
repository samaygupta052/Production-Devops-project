from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
def health_check():
    return {"status": "healthy"}

@router.get("/api/message")
def get_message():
    return {"message": "Hello from FastAPI backend"}

@router.get("/memory-spike")
def memory_spike():
    data = []
    for i in range(10**7):
        data.append("consume-memory")
    return {"status": "memory consumed"}

@router.get("/version")
def version():
    return {"version": "canary"}

