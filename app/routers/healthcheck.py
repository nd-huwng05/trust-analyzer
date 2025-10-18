from fastapi import FastAPI, APIRouter

router = APIRouter(prefix="/health", tags=["healthcheck"])

@router.get("/check")
def health_check():
    return {"status": "ok"}