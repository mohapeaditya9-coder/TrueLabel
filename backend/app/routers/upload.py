from fastapi import APIRouter

router = APIRouter(prefix="/upload", tags=["Upload"])


@router.get("/")
def upload_status():
    return {"message": "Upload router active"}
