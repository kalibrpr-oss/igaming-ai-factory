from fastapi import APIRouter

from app.prompts.registry import list_brand_voices_meta

router = APIRouter()


@router.get("")
def get_brand_voices() -> dict[str, list[dict[str, str]]]:
    items = list_brand_voices_meta()
    return {
        "items": [
            {"id": m.id, "label": m.label, "description": m.description} for m in items
        ]
    }
