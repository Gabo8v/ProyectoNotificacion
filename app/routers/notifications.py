from fastapi import APIRouter

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.post("/send")
def send_notification():
    return {"message": "Not implemented yet"}


@router.get("/history")
def get_history():
    return {"message": "Not implemented yet"}
