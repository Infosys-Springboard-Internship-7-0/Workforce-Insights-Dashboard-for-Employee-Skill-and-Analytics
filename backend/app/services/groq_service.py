from groq import Groq
from app.core.config import get_settings

settings = get_settings()
client = Groq(api_key=settings.groq_api_key)


SYSTEM_PROMPT = """You are the AI-Powered Workforce Analytics & Talent Intelligence Dashboard.

Answer questions using the supplied project context.

Rules:
1. Use the provided context for project-specific claims.
2. Do not invent facts that are not in the context.
3. If the context does not contain the answer, say so clearly.
4. Be concise and professional.
5. When sources are supplied, use them as evidence.
"""


def generate_answer(question: str, context: str) -> str:
    completion = client.chat.completions.create(
        model=settings.groq_model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"""Context:
{context}

Question:
{question}
""",
            },
        ],
        temperature=0.2,
        max_tokens=1200,
    )
    return completion.choices[0].message.content or "No answer was generated."
