from abc import ABC, abstractmethod

from dataclasses import dataclass





@dataclass(frozen=True)

class BrandVoiceMeta:

    id: str

    label: str

    description: str





class BrandVoicePrompt(ABC):

    """Один голос = один модуль в prompts/voices/. Сборка system — через system.assembler."""



    meta: BrandVoiceMeta



    @abstractmethod

    def build_system_prompt(self) -> str: ...



    @abstractmethod

    def build_user_prompt(

        self, brand: str, keywords: list[str], extra: str | None

    ) -> str: ...


