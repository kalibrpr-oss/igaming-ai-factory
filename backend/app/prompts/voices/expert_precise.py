from app.prompts.base import BrandVoiceMeta, BrandVoicePrompt


class ExpertPreciseVoice(BrandVoicePrompt):
    meta = BrandVoiceMeta(
        id="expert_precise",
        label="Expert",
        description="Аналитик гемблинга: факты, структура, цифры — без сленга и эмоций.",
    )

    def build_system_prompt(self) -> str:
        return (
            "Ты аналитик гемблинга.\n"
            "Тон: спокойный, точный.\n"
            "Манера: логика, факты, структура.\n"
            "Приёмы: цифры; анализ поведения слота; чёткие выводы.\n"
            "Запреты: эмоции; сленг; разговорная подача.\n"
            "Требования: чётко, структурно, без воды, всегда по теме слотов и игры.\n"
            "Формат выхода: готовый текст без преамбулы."
        )

    def build_user_prompt(
        self, brand: str, keywords: list[str], extra: str | None
    ) -> str:
        keys = ", ".join(keywords)
        tail = f"\nДоп. ТЗ: {extra}" if extra else ""
        return f"Бренд: {brand}\nКлючи и LSI: {keys}{tail}"
