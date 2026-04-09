from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.prompts.registry import get_voice
from app.services.llm.demo_rewrite import rewrite_demo_text

router = APIRouter()


class DemoRewriteBody(BaseModel):
    text: str = Field(min_length=10, max_length=4000)
    voice_id: str = Field(min_length=1, max_length=64)


class DemoRewriteResponse(BaseModel):
    result: str


@router.post("/rewrite", response_model=DemoRewriteResponse)
async def demo_rewrite(body: DemoRewriteBody) -> DemoRewriteResponse:
    try:
        get_voice(body.voice_id)
    except KeyError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    try:
        text = await rewrite_demo_text(body.text, body.voice_id)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(
            status_code=502, detail=f"Ошибка модели: {e!s}"
        ) from e

    return DemoRewriteResponse(result=text)
