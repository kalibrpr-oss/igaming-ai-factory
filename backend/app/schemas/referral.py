from pydantic import BaseModel, Field


class ReferralSummaryResponse(BaseModel):
    """Сводка для личного кабинета."""

    referral_code: str
    referral_link_query: str  # "?ref=code" — клеится к origin на фронте
    slug_locked: bool
    referrals_count: int
    rewards_total_cents: int


class ReferralCodeUpdateBody(BaseModel):
    """Один раз задать красивый slug (если ещё не locked)."""

    code: str = Field(min_length=4, max_length=32)
