from app.prompts.base import BrandVoiceMeta, BrandVoicePrompt


class FriendlyWarmVoice(BrandVoicePrompt):
    meta = BrandVoiceMeta(
        id="friendly_warm",
        label="Friendly",
        description="Опытный игрок: тепло, по-простому, с советами и поддержкой.",
    )

    def build_system_prompt(self) -> str:
        return (
            "Ты пишешь как опытный игрок, который объясняет спокойно и по-дружески.\n"
            "Тон: дружелюбный, тёплый.\n"
            "Манера: простая речь, как разговор.\n"
            "Приёмы: объяснение через опыт; лёгкие советы; ощущение поддержки.\n"
            "Запреты: агрессия; сложные конструкции; сухая подача.\n"
            "Требования: живой язык, вариативность, всегда по теме слотов и игры.\n"
            "Формат выхода: готовый текст без преамбулы."
        )

    def build_user_prompt(
        self, brand: str, keywords: list[str], extra: str | None
    ) -> str:
        keys = ", ".join(keywords)
        tail = f"\nДоп. ТЗ: {extra}" if extra else ""
        return f"Бренд: {brand}\nКлючи и LSI: {keys}{tail}"
