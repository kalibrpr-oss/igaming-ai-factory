from typing import Type

from app.prompts.base import BrandVoiceMeta, BrandVoicePrompt
from app.prompts.voices.bold_daring import BoldDaringVoice
from app.prompts.voices.expert_precise import ExpertPreciseVoice
from app.prompts.voices.friendly_warm import FriendlyWarmVoice

_REGISTRY: dict[str, Type[BrandVoicePrompt]] = {
    BoldDaringVoice.meta.id: BoldDaringVoice,
    ExpertPreciseVoice.meta.id: ExpertPreciseVoice,
    FriendlyWarmVoice.meta.id: FriendlyWarmVoice,
}


def list_brand_voices_meta() -> list[BrandVoiceMeta]:
    return [cls.meta for cls in _REGISTRY.values()]


def get_voice(voice_id: str) -> BrandVoicePrompt:
    cls = _REGISTRY.get(voice_id)
    if not cls:
        raise KeyError(f"Неизвестный голос: {voice_id}")
    return cls()
