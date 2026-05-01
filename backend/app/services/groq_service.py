from groq import Groq
from typing import List, Dict
from app.config import settings
import json
import re

class GroqService:
    def __init__(self):
        self.api_key = settings.GROQ_API_KEY
        if self.api_key:
            self.client = Groq(api_key=self.api_key)
        else:
            self.client = None

        # Модель DeepSeek-R1-Distill-Llama-70B
        self.model = "deepseek-r1-distill-llama-70b"
        # Оптимальная температура для DeepSeek (рекомендация Groq)
        self.temperature = 0.6

    def _clean_json_response(self, response_text: str) -> str:
        """
        Очищает ответ от XML-тегов, markdown блоков и лишнего текста
        """
        # Убираем XML теги <function=json>...</function>
        response_text = re.sub(r'<function[^>]*>|</function>', '', response_text)

        # Убираем markdown код блоки
        if response_text.startswith("```"):
            lines = response_text.split('\n')
            # Убираем первую строку (```json или ```javascript) и последнюю (```)
            response_text = '\n'.join(lines[1:-1]) if len(lines) > 2 else response_text

        # Убираем возможные префиксы типа "json" или "javascript"
        response_text = re.sub(r'^(json|javascript)\s*', '', response_text.strip())

        return response_text.strip()

    def _validate_quiz_card(self, card: Dict) -> bool:
        """
        Валидирует структуру quiz карточки
        """
        required_fields = ["question", "options", "correct_answer", "explanation"]

        # Проверяем наличие всех полей
        if not all(field in card for field in required_fields):
            return False

        # Проверяем что correct_answer это число от 0 до 3
        if not isinstance(card["correct_answer"], int) or card["correct_answer"] not in [0, 1, 2, 3]:
            return False

        # Проверяем что options это список из 4 элементов
        if not isinstance(card["options"], list) or len(card["options"]) != 4:
            return False

        # Проверяем что все поля заполнены
        if not card["question"] or not card["explanation"]:
            return False

        if not all(option for option in card["options"]):
            return False

        return True

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

        max_retries = 2
        for attempt in range(max_retries):
            try:
                prompt = f"""Сгенерируй ТОЛЬКО {count} неправильных, но правдоподобных варианта ответа.

Вопрос: {question}
Правильный ответ: {correct_answer}

ТРЕБОВАНИЯ:
- Варианты должны быть похожи на правильный ответ
- Каждый вариант с новой строки
- БЕЗ нумерации, БЕЗ дополнительного текста
- НЕ оборачивай ответ в теги `function` или `xml`
- Только {count} варианта"""

                chat_completion = self.client.chat.completions.create(
                    messages=[
                        {
                            "role": "user",
                            "content": prompt,
                        }
                    ],
                    model=self.model,
                    temperature=self.temperature,
                    max_tokens=200,
                )

                response_text = chat_completion.choices[0].message.content
                response_text = self._clean_json_response(response_text)

                wrong_answers = [line.strip() for line in response_text.strip().split('\n') if line.strip()]

                # Валидация: должно быть хотя бы count ответов
                if len(wrong_answers) >= count:
                    return wrong_answers[:count]

                # Если недостаточно - повторяем попытку
                if attempt < max_retries - 1:
                    continue

            except Exception as e:
                print(f"Groq API error (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    continue

        return []

    async def generate_quiz_cards(
        self,
        topic: str,
        details: str = "",
        count: int = 5
    ) -> List[Dict]:
        """
        Генерирует полные Quiz карточки по теме через Groq API
        Использует новый формат с options и correct_answer как индекс
        """
        if not self.client:
            return []

        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Формируем промпт согласно новым требованиям
                prompt = f"""Сгенерируй ТОЛЬКО валидный JSON-массив с {count} вопросами-квизами.

Тема: {topic}
Подробности от пользователя: {details if details.strip() else "Нет дополнительных деталей"}

Каждый объект вопроса должен иметь вид:
{{
    "question": "...",
    "options": ["...", "...", "...", "..."],
    "correct_answer": 0,
    "explanation": "..."
}}

ТРЕБОВАНИЯ:
- Ответ должен быть ТОЛЬКО чистым JSON, никаких пояснений до или после.
- НЕ оборачивай JSON в теги `function` или `xml`.
- `correct_answer` — это числовой индекс (0-3) правильного варианта в массиве options.
- `explanation` (объяснение) обязательно и должно быть на русском языке.
- Все 4 варианта ответов должны быть правдоподобными, но только один правильный.
- Вопросы должны быть разнообразными и охватывать разные аспекты темы."""

                chat_completion = self.client.chat.completions.create(
                    messages=[
                        {
                            "role": "user",
                            "content": prompt,
                        }
                    ],
                    model=self.model,
                    temperature=self.temperature,
                    max_tokens=3000,
                    response_format={"type": "json_object"}
                )

                response_text = chat_completion.choices[0].message.content.strip()
                response_text = self._clean_json_response(response_text)

                # Парсим JSON
                parsed_data = json.loads(response_text)

                # Если ответ обернут в объект с ключом (например {"questions": [...]})
                if isinstance(parsed_data, dict) and not all(k in parsed_data for k in ["question", "options"]):
                    # Ищем массив в значениях
                    for value in parsed_data.values():
                        if isinstance(value, list):
                            parsed_data = value
                            break

                # Если это не список - оборачиваем
                if not isinstance(parsed_data, list):
                    parsed_data = [parsed_data]

                # Валидация каждой карточки
                valid_cards = []
                for card in parsed_data:
                    if self._validate_quiz_card(card):
                        # Конвертируем в старый формат для совместимости
                        correct_index = card["correct_answer"]
                        correct_answer_text = card["options"][correct_index]
                        wrong_answers = [opt for i, opt in enumerate(card["options"]) if i != correct_index]

                        valid_cards.append({
                            "question": card["question"],
                            "correct_answer": correct_answer_text,
                            "wrong_answers": wrong_answers[:3],  # Берем только 3
                            "explanation": card["explanation"]
                        })

                # Если получили достаточно валидных карточек - возвращаем
                if len(valid_cards) >= count:
                    return valid_cards[:count]

                # Если недостаточно - повторяем попытку
                if attempt < max_retries - 1:
                    print(f"Недостаточно валидных карточек ({len(valid_cards)}/{count}), повторная попытка...")
                    continue

                # На последней попытке возвращаем что есть
                return valid_cards

            except json.JSONDecodeError as e:
                print(f"JSON parse error (attempt {attempt + 1}): {e}")
                print(f"Response text: {response_text[:200]}...")
                if attempt < max_retries - 1:
                    continue
            except Exception as e:
                print(f"Groq API error (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    continue

        return []

groq_service = GroqService()
