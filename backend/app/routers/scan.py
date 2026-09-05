from fastapi import APIRouter

router = APIRouter(prefix="/scan", tags=["Scan"])


@router.get("/")
def scan_status():
    return {"message": "Scan router active"}
