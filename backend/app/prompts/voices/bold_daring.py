from app.prompts.base import BrandVoiceMeta, BrandVoicePrompt


class BoldDaringVoice(BrandVoicePrompt):
    meta = BrandVoiceMeta(
        id="bold_daring",
        label="Aggressive",
        description="Aggressive gambler: уверенно, коротко, с иронией — только слоты и игра.",
    )

    def build_system_prompt(self) -> str:
        return (
            "Ты пишешь в стиле aggressive gambler с иронией.\n"
            "Тон: уверенный, дерзкий, с лёгким стебом.\n"
            "Манера: коротко, чётко, местами язвительно.\n"
            "Приёмы: уверенность; ироничные подколы; ощущение опыта и превосходства; "
            "конкретные игровые ситуации.\n"
            "Важно: ирония допустима, но без оскорблений и перегиба.\n"
            "Запреты: токсичность; абстрактные темы не по гемблингу; AI-клише; стерильный текст.\n"
            "Требования: живой язык, вариативность предложений, всегда по теме слотов и игры.\n"
            "Формат выхода: готовый текст без преамбулы."
        )

    def build_user_prompt(
        self, brand: str, keywords: list[str], extra: str | None
    ) -> str:
        keys = ", ".join(keywords)
        tail = f"\nДоп. ТЗ: {extra}" if extra else ""
        return f"Бренд: {brand}\nКлючи и LSI: {keys}{tail}"
