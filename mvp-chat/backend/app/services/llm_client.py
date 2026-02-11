from typing import AsyncGenerator
from openai import OpenAI

from app.core.config import settings


class LLMClient:
    def __init__(self) -> None:
        # toma OPENAI_API_KEY del entorno automáticamente
        self.client = OpenAI(
            api_key=settings.openai_api_key
        )

    async def stream_reply(self, messages: list[dict]) -> AsyncGenerator[str, None]:
        """
        messages: [{"role":"system"|"user"|"assistant", "content": "..."}]
        """
        if not messages or messages[0]["role"] != "system":
            raise ValueError("messages debe iniciar con role=system")

        instructions = messages[0]["content"]
        input_items = [{"role": m["role"], "content": m["content"]} for m in messages[1:]]

        stream = self.client.responses.create(
            model=settings.openai_model,
            instructions=instructions,
            input=input_items,
            stream=True,
        )

        # En Responses streaming, lo útil para texto es:
        # - response.output_text.delta (delta incremental)
        # - response.refusal.delta (si el modelo se niega)
        for event in stream:
            etype = getattr(event, "type", None) or (event.get("type") if isinstance(event, dict) else None)

            if etype == "response.output_text.delta":
                delta = getattr(event, "delta", None) or (event.get("delta") if isinstance(event, dict) else "")
                if delta:
                    yield delta

            elif etype == "response.refusal.delta":
                delta = getattr(event, "delta", None) or (event.get("delta") if isinstance(event, dict) else "")
                if delta:
                    yield delta

            elif etype == "error":
                # deja que falle: tu SSE lo verá como excepción si no lo capturas arriba
                raise RuntimeError(str(event))
