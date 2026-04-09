from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def v1_health() -> dict[str, str]:
    return {"api": "v1", "status": "ok"}
