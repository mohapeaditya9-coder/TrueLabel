from fastapi import APIRouter

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/")
def reports_status():
    return {"message": "Reports router active"}
