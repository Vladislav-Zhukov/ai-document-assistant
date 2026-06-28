import json

from app.services.llm import OpenRouterProvider


class DocumentClassifierService:
    def __init__(self):
        self.llm_provider = OpenRouterProvider()

    async def classify(self, text: str) -> tuple[str, float]:
        sample = text[:6000]

        prompt = f"""
Classify the document into one of these categories:

- contract
- invoice
- resume
- report
- manual
- article
- other

Return ONLY valid JSON:
{{
  "document_type": "contract",
  "confidence": 0.95
}}

Document text:
{sample}
"""

        response = await self.llm_provider.generate_raw(prompt)

        try:
            data = json.loads(response)
            return (
                data.get("document_type", "other"),
                float(data.get("confidence", 0.0)),
            )
        except Exception:
            return "other", 0.0