from fastapi import APIRouter

router = APIRouter(prefix="/templates", tags=["templates"])


@router.get("/")
def list_templates():
    return {"message": "Not implemented yet"}


@router.post("/")
def create_template():
    return {"message": "Not implemented yet"}
