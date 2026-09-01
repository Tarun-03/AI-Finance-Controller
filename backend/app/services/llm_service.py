from typing import Any

from app.core.config import settings


class LLMService:
    """
    Provider-independent LLM abstraction.

    Phase 3B starts with a deterministic fallback.
    A real provider can be plugged in later without
    changing the agent graph.
    """

    def __init__(self):
        self.provider = settings.LLM_PROVIDER
        self.model = settings.LLM_MODEL

        self.llm = self._create_llm()

    def _create_llm(self) -> Any:
        if self.provider == "none":
            return None

        raise ValueError(
            f"Unsupported LLM provider: {self.provider}"
        )

    def analyze_exception(
        self,
        context: dict,
    ) -> dict:

        if self.llm is None:
            return self._fallback_analysis(context)

        raise NotImplementedError(
            "LLM provider integration will be added "
            "in the next phase."
        )

    @staticmethod
    def _fallback_analysis(
        context: dict,
    ) -> dict:

        difference = context.get(
            "difference",
            0,
        )

        exception_type = context.get(
            "exception_type",
            "UNKNOWN",
        )

        severity = context.get(
            "severity",
            "UNKNOWN",
        )

        return {
            "analysis": (
                f"{exception_type} detected with "
                f"{severity} severity and a difference "
                f"of {difference}."
            ),
            "recommended_action": context.get(
                "recommendation",
                "HUMAN_REVIEW",
            ),
            "confidence": 0.50,
        }