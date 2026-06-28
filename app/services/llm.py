from openai import AsyncOpenAI

from app.core.config import settings


class LLMProvider:
    async def generate_answer(
        self,
        question: str,
        context_chunks: list[str],
    ) -> str:
        raise NotImplementedError


class MockLLMProvider(LLMProvider):
    async def generate_answer(
            self,
            question: str,
            context_chunks: list[str],
            chat_history: list[dict] | None = None,
    ) -> str:
        context = "\n\n".join(context_chunks)

        return (
            "Mock AI answer.\n\n"
            f"Question: {question}\n\n"
            "Relevant context from document:\n"
            f"{context[:1500]}"
        )


class OpenRouterProvider(LLMProvider):
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL,
            timeout=120.0,
        )

    async def generate_answer(
            self,
            question: str,
            context_chunks: list[str],
            chat_history: list[dict] | None = None,
    ) -> str:
        context = "\n\n---\n\n".join(context_chunks)

        messages = [
            {
                "role": "system",
                "content": (
                    "You are an AI document assistant. "
                    "Answer only using the provided document context. "
                    "If the answer is not present in the context, say: "
                    "\"I don't know based on the provided document.\""
                ),
            }
        ]

        if chat_history:
            messages.extend(chat_history)

        prompt = f"""
    Document context:
    {context}

    User question:
    {question}
    """

        messages.append(
            {
                "role": "user",
                "content": prompt,
            }
        )

        response = await self.client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=messages,
            temperature=settings.LLM_TEMPERATURE,
        )

        return response.choices[0].message.content or ""

    async def stream_answer(
            self,
            question: str,
            context_chunks: list[str],
            chat_history: list[dict] | None = None,
    ):
        context = "\n\n---\n\n".join(context_chunks)

        messages = [
            {
                "role": "system",
                "content": (
                    "You are an AI document assistant. "
                    "Answer only using the provided document context. "
                    "If the answer is not present in the context, say: "
                    "\"I don't know based on the provided document.\""
                ),
            }
        ]

        if chat_history:
            messages.extend(chat_history)

        prompt = f"""
    Document context:
    {context}

    User question:
    {question}
    """

        messages.append({"role": "user", "content": prompt})

        stream = await self.client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=messages,
            temperature=settings.LLM_TEMPERATURE,
            stream=True,
        )

        async for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta

    async def generate_summary(
            self,
            context_chunks: list[str],
    ) -> str:
        context = "\n\n---\n\n".join(context_chunks)

        prompt = f"""
    Сделай краткое резюме документа, используя ТОЛЬКО предоставленный контекст.

    Контекст документа:
    {context}

    Требования к резюме:
    - отвечай на русском языке
    - 5-10 предложений
    - укажи основную тему документа
    - укажи ключевые факты
    - не выдумывай информацию
    """

        response = await self.client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Ты помощник для краткого пересказа документов. "
                        "Всегда отвечай на русском языке."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            temperature=settings.LLM_TEMPERATURE,
        )

        return response.choices[0].message.content or ""

    async def generate_raw(self, prompt: str) -> str:
        response = await self.client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            temperature=0,
        )

        return response.choices[0].message.content or ""