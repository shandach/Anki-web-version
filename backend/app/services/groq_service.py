from groq import Groq
from typing import List, Dict
from app.config import settings
import json

class GroqService:
    def __init__(self):
        self.api_key = settings.GROQ_API_KEY
        if self.api_key:
            self.client = Groq(api_key=self.api_key)
        else:
            self.client = None

    async def generate_wrong_answers(
        self,
        question: str,
        correct_answer: str,
        count: int = 3
    ) -> List[str]:
        """
        Генерирует неправильные варианты ответов через Groq API
        """
        if not self.client:
            return []

        try:
            prompt = f"""Вопрос: {question}
Правильный ответ: {correct_answer}

Сгенерируй {count} неправильных, но правдоподобных варианта ответа на этот вопрос.
Варианты должны быть похожи на правильный ответ, чтобы создать сложность выбора.
Верни только варианты ответов, каждый с новой строки, без нумерации и дополнительного текста."""

            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model="llama-3.3-70b-versatile",
                temperature=0.7,
                max_tokens=200,
            )

            response_text = chat_completion.choices[0].message.content
            wrong_answers = [line.strip() for line in response_text.strip().split('\n') if line.strip()]

            # Берем только нужное количество
            return wrong_answers[:count]

        except Exception as e:
            print(f"Groq API error: {e}")
            return []

    async def generate_quiz_cards(
        self,
        topic: str,
        details: str = "",
        count: int = 5
    ) -> List[Dict]:
        """
        Генерирует полные Quiz карточки по теме через Groq API
        """
        if not self.client:
            return []

        try:
            # Формируем промпт с учетом деталей
            base_prompt = f"""Создай {count} тестовых вопросов по теме: {topic}"""

            if details.strip():
                base_prompt += f"\n\nДополнительные требования и детали:\n{details}"

            prompt = base_prompt + """

Для каждого вопроса создай:
1. Вопрос
2. Один правильный ответ
3. Три неправильных, но правдоподобных варианта ответа

Верни результат СТРОГО в формате JSON массива:
[
  {{
    "question": "текст вопроса",
    "correct_answer": "правильный ответ",
    "wrong_answers": ["неправильный 1", "неправильный 2", "неправильный 3"]
  }}
]

Важно: верни ТОЛЬКО JSON массив, без дополнительного текста."""

            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model="llama-3.3-70b-versatile",
                temperature=0.8,
                max_tokens=2000,
            )

            response_text = chat_completion.choices[0].message.content.strip()

            # Убираем markdown код блоки если есть
            if response_text.startswith("```"):
                lines = response_text.split('\n')
                response_text = '\n'.join(lines[1:-1])

            # Парсим JSON
            quiz_data = json.loads(response_text)

            return quiz_data[:count]

        except Exception as e:
            print(f"Groq API error: {e}")
            return []

groq_service = GroqService()
