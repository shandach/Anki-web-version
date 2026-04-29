import api from './api';

export const quizAPI = {
  // Получить все Quiz карточки колоды
  getAll: (deckId: number) => api.get(`/quiz/decks/${deckId}/cards`),

  // Получить прогресс Quiz для колоды
  getProgress: (deckId: number) => api.get(`/quiz/decks/${deckId}/progress`),

  // Создать Quiz карточку
  create: (deckId: number, data: {
    question: string;
    correct_answers: string[];
    wrong_answers?: string[];
    source_deck_id?: number;
    is_multiple: boolean;
    generate_wrong_with_ai: boolean;
  }) => api.post(`/quiz/decks/${deckId}/cards`, data),

  // Массовая генерация Quiz карточек через AI
  bulkGenerate: (deckId: number, data: {
    topic: string;
    details?: string;
    count: number;
    create_new_deck?: boolean;
  }) => api.post(`/quiz/decks/${deckId}/cards/bulk-generate`, data),

  // Получить следующую карточку для изучения
  getNext: (deckId: number) => api.get(`/quiz/study/${deckId}/next`),

  // Отправить ответ
  submitAnswer: (cardId: number, selectedAnswers: string[]) =>
    api.post(`/quiz/study/review/${cardId}`, { selected_answers: selectedAnswers }),

  // Удалить карточку
  delete: (cardId: number) => api.delete(`/quiz/cards/${cardId}`),
};
