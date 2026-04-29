'use client';

import { useEffect, useState } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { decksAPI, cardsAPI } from '@/lib/api';
import { quizAPI } from '@/lib/quiz-api';
import { Deck, Card } from '@/lib/types';
import { QuizCard } from '@/lib/quiz-types';

export default function DeckDetailPage() {
  const router = useRouter();
  const params = useParams();
  const deckId = Number(params.id);

  const [deck, setDeck] = useState<Deck | null>(null);
  const [cards, setCards] = useState<Card[]>([]);
  const [quizCards, setQuizCards] = useState<QuizCard[]>([]);
  const [quizProgress, setQuizProgress] = useState<{total_cards: number, answered_cards: number, progress_percentage: number} | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'regular' | 'quiz'>('regular');
  const [showAddModal, setShowAddModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showAddQuizModal, setShowAddQuizModal] = useState(false);
  const [quizCreationMode, setQuizCreationMode] = useState<'manual' | 'ai'>('manual');
  const [editingCard, setEditingCard] = useState<Card | null>(null);
  const [newFront, setNewFront] = useState('');
  const [newBack, setNewBack] = useState('');

  // Quiz card form state - manual mode
  const [quizQuestion, setQuizQuestion] = useState('');
  const [correctAnswers, setCorrectAnswers] = useState<string[]>(['']);
  const [wrongAnswers, setWrongAnswers] = useState<string[]>(['', '', '']);
  const [isMultiple, setIsMultiple] = useState(false);
  const [generateWithAI, setGenerateWithAI] = useState(false);
  const [sourceDeckId, setSourceDeckId] = useState<number | undefined>(undefined);
  const [allDecks, setAllDecks] = useState<Deck[]>([]);

  // Quiz card form state - AI mode
  const [aiTopic, setAiTopic] = useState('');
  const [aiDetails, setAiDetails] = useState('');
  const [aiCount, setAiCount] = useState(5);
  const [isGenerating, setIsGenerating] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      router.push('/login');
      return;
    }

    loadDeck();
    loadCards();
    loadQuizCards();
    loadQuizProgress();
    loadAllDecks();
  }, []);

  const loadDeck = async () => {
    try {
      const response = await decksAPI.getOne(deckId);
      setDeck(response.data);
    } catch (err) {
      console.error('Failed to load deck', err);
    }
  };

  const loadCards = async () => {
    try {
      const response = await cardsAPI.getAll(deckId);
      setCards(response.data);
    } catch (err) {
      console.error('Failed to load cards', err);
    } finally {
      setLoading(false);
    }
  };

  const loadQuizCards = async () => {
    try {
      const response = await quizAPI.getAll(deckId);
      setQuizCards(response.data);
    } catch (err) {
      console.error('Failed to load quiz cards', err);
    }
  };

  const loadQuizProgress = async () => {
    try {
      const response = await quizAPI.getProgress(deckId);
      setQuizProgress(response.data);
    } catch (err) {
      console.error('Failed to load quiz progress', err);
    }
  };

  const loadAllDecks = async () => {
    try {
      const response = await decksAPI.getAll();
      setAllDecks(response.data);
    } catch (err) {
      console.error('Failed to load decks', err);
    }
  };

  const handleAddCard = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await cardsAPI.create(deckId, { front: newFront, back: newBack });
      setShowAddModal(false);
      setNewFront('');
      setNewBack('');
      loadCards();
      loadDeck();
    } catch (err) {
      console.error('Failed to create card', err);
    }
  };

  const handleEditCard = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingCard) return;

    try {
      await cardsAPI.update(editingCard.id, { front: newFront, back: newBack });
      setShowEditModal(false);
      setEditingCard(null);
      setNewFront('');
      setNewBack('');
      loadCards();
    } catch (err) {
      console.error('Failed to update card', err);
    }
  };

  const handleDeleteCard = async (cardId: number) => {
    if (!confirm('Вы уверены, что хотите удалить эту карточку?')) return;

    try {
      await cardsAPI.delete(cardId);
      loadCards();
      loadDeck();
    } catch (err) {
      console.error('Failed to delete card', err);
    }
  };

  const openEditModal = (card: Card) => {
    setEditingCard(card);
    setNewFront(card.front);
    setNewBack(card.back);
    setShowEditModal(true);
  };

  const handleAddQuizCard = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const filteredCorrect = correctAnswers.filter(a => a.trim() !== '');
      const filteredWrong = wrongAnswers.filter(a => a.trim() !== '');

      await quizAPI.create(deckId, {
        question: quizQuestion,
        correct_answers: filteredCorrect,
        wrong_answers: filteredWrong.length > 0 ? filteredWrong : undefined,
        source_deck_id: sourceDeckId,
        is_multiple: isMultiple,
        generate_wrong_with_ai: generateWithAI
      });

      setShowAddQuizModal(false);
      resetQuizForm();
      loadQuizCards();
    } catch (err) {
      console.error('Failed to create quiz card', err);
      alert('Ошибка при создании Quiz карточки. Проверьте, что добавлен GROQ_API_KEY в .env файл.');
    }
  };

  const handleBulkGenerateQuizCards = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!aiTopic.trim()) {
      alert('Укажите тему для генерации');
      return;
    }

    try {
      setIsGenerating(true);
      const response = await quizAPI.bulkGenerate(deckId, {
        topic: aiTopic,
        details: aiDetails,
        count: aiCount,
        create_new_deck: true
      });

      setShowAddQuizModal(false);
      resetQuizForm();

      // Перенаправляем на страницу колод, чтобы увидеть новую Quiz-колоду
      alert(`Успешно создана новая Quiz-колода "${aiTopic}" с ${aiCount} вопросами!`);
      router.push('/decks');
    } catch (err) {
      console.error('Failed to generate quiz cards', err);
      alert('Ошибка при генерации Quiz карточек. Проверьте, что добавлен GROQ_API_KEY в .env файл.');
    } finally {
      setIsGenerating(false);
    }
  };

  const handleDeleteQuizCard = async (cardId: number) => {
    if (!confirm('Вы уверены, что хотите удалить эту Quiz карточку?')) return;

    try {
      await quizAPI.delete(cardId);
      loadQuizCards();
    } catch (err) {
      console.error('Failed to delete quiz card', err);
    }
  };

  const resetQuizForm = () => {
    setQuizQuestion('');
    setCorrectAnswers(['']);
    setWrongAnswers(['', '', '']);
    setIsMultiple(false);
    setGenerateWithAI(false);
    setSourceDeckId(undefined);
    setAiTopic('');
    setAiDetails('');
    setAiCount(5);
    setQuizCreationMode('manual');
  };

  const addCorrectAnswer = () => {
    setCorrectAnswers([...correctAnswers, '']);
  };

  const updateCorrectAnswer = (index: number, value: string) => {
    const updated = [...correctAnswers];
    updated[index] = value;
    setCorrectAnswers(updated);
  };

  const removeCorrectAnswer = (index: number) => {
    if (correctAnswers.length > 1) {
      setCorrectAnswers(correctAnswers.filter((_, i) => i !== index));
    }
  };

  const updateWrongAnswer = (index: number, value: string) => {
    const updated = [...wrongAnswers];
    updated[index] = value;
    setWrongAnswers(updated);
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-xl text-gray-900 font-medium">Загрузка...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-bold text-gray-900">Anki Web</h1>
            </div>
            <div className="flex items-center space-x-4">
              <a href="/dashboard" className="text-gray-900 hover:text-blue-600 font-medium">
                Панель
              </a>
              <a href="/decks" className="text-gray-900 hover:text-blue-600 font-medium">
                Колоды
              </a>
              <button
                onClick={() => {
                  localStorage.removeItem('token');
                  router.push('/login');
                }}
                className="text-gray-900 hover:text-blue-600 font-medium"
              >
                Выйти
              </button>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          {/* Header */}
          <div className="bg-white p-6 rounded-lg shadow mb-6">
            <div className="flex justify-between items-start">
              <div>
                <h2 className="text-3xl font-bold text-gray-900 mb-2">{deck?.name}</h2>
                <p className="text-gray-700 mb-4">{deck?.description}</p>
                <div className="flex space-x-4 text-sm text-gray-600">
                  <span className="font-medium">Всего карточек: {cards.length}</span>
                  <span className="font-medium">Quiz карточек: {quizCards.length}</span>
                  <span className="text-blue-600 font-medium">К изучению: {deck?.due_cards_count || 0}</span>
                </div>
                {quizProgress && quizProgress.total_cards > 0 && (
                  <div className="mt-3">
                    <div className="flex items-center space-x-3">
                      <span className="text-sm font-medium text-purple-600">
                        Quiz прогресс: {quizProgress.answered_cards} / {quizProgress.total_cards} ({quizProgress.progress_percentage}%)
                      </span>
                      <div className="flex-1 max-w-xs bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-purple-600 h-2 rounded-full transition-all"
                          style={{ width: `${quizProgress.progress_percentage}%` }}
                        ></div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
              <div className="flex space-x-2">
                {(deck?.due_cards_count || 0) > 0 && (
                  <a
                    href={`/study/${deckId}`}
                    className="px-6 py-3 bg-blue-600 text-white rounded-md hover:bg-blue-700 font-medium shadow-sm"
                  >
                    Начать изучение
                  </a>
                )}
                {quizCards.length > 0 && (
                  <a
                    href={`/quiz-study/${deckId}`}
                    className="px-6 py-3 bg-purple-600 text-white rounded-md hover:bg-purple-700 font-medium shadow-sm"
                  >
                    {quizProgress && quizProgress.answered_cards > 0 ? 'Продолжить Quiz' : 'Quiz режим'}
                  </a>
                )}
              </div>
            </div>
          </div>

          {/* Tabs */}
          <div className="bg-white rounded-lg shadow mb-6">
            <div className="border-b border-gray-200">
              <nav className="flex -mb-px">
                <button
                  onClick={() => setActiveTab('regular')}
                  className={`px-6 py-4 text-sm font-medium border-b-2 ${
                    activeTab === 'regular'
                      ? 'border-blue-600 text-blue-600'
                      : 'border-transparent text-gray-600 hover:text-gray-900 hover:border-gray-300'
                  }`}
                >
                  Обычные карточки ({cards.length})
                </button>
                <button
                  onClick={() => setActiveTab('quiz')}
                  className={`px-6 py-4 text-sm font-medium border-b-2 ${
                    activeTab === 'quiz'
                      ? 'border-purple-600 text-purple-600'
                      : 'border-transparent text-gray-600 hover:text-gray-900 hover:border-gray-300'
                  }`}
                >
                  Quiz карточки ({quizCards.length})
                </button>
              </nav>
            </div>
          </div>

          {/* Cards List */}
          {activeTab === 'regular' ? (
            <>
              <div className="flex justify-end mb-4">
                <button
                  onClick={() => setShowAddModal(true)}
                  className="px-6 py-3 bg-green-600 text-white rounded-md hover:bg-green-700 font-medium shadow-sm"
                >
                  Добавить карточку
                </button>
              </div>
              {cards.length === 0 ? (
                <div className="bg-white p-12 rounded-lg shadow text-center">
                  <p className="text-gray-600 text-lg mb-4">В этой колоде пока нет карточек</p>
                  <button
                    onClick={() => setShowAddModal(true)}
                    className="px-6 py-3 bg-green-600 text-white rounded-md hover:bg-green-700 font-medium"
                  >
                    Добавить первую карточку
                  </button>
                </div>
              ) : (
                <div className="space-y-4">
                  {cards.map((card) => (
                    <div key={card.id} className="bg-white p-6 rounded-lg shadow hover:shadow-lg transition-shadow">
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div>
                          <div className="text-sm text-gray-600 font-medium mb-2">Вопрос</div>
                          <div className="text-gray-900 font-medium">{card.front}</div>
                        </div>
                        <div>
                          <div className="text-sm text-gray-600 font-medium mb-2">Ответ</div>
                          <div className="text-gray-900">{card.back}</div>
                        </div>
                      </div>
                      <div className="mt-4 flex justify-end space-x-2">
                        <button
                          onClick={() => openEditModal(card)}
                          className="px-4 py-2 bg-blue-100 text-blue-700 rounded hover:bg-blue-200 font-medium"
                        >
                          Редактировать
                        </button>
                        <button
                          onClick={() => handleDeleteCard(card.id)}
                          className="px-4 py-2 bg-red-100 text-red-700 rounded hover:bg-red-200 font-medium"
                        >
                          Удалить
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </>
          ) : (
            <>
              <div className="flex justify-end mb-4">
                <button
                  onClick={() => setShowAddQuizModal(true)}
                  className="px-6 py-3 bg-purple-600 text-white rounded-md hover:bg-purple-700 font-medium shadow-sm"
                >
                  Добавить Quiz карточку
                </button>
              </div>
              {quizCards.length === 0 ? (
                <div className="bg-white p-12 rounded-lg shadow text-center">
                  <p className="text-gray-600 text-lg mb-4">В этой колоде пока нет Quiz карточек</p>
                  <button
                    onClick={() => setShowAddQuizModal(true)}
                    className="px-6 py-3 bg-purple-600 text-white rounded-md hover:bg-purple-700 font-medium"
                  >
                    Добавить первую Quiz карточку
                  </button>
                </div>
              ) : (
                <div className="space-y-4">
                  {quizCards.map((card) => (
                    <div key={card.id} className="bg-white p-6 rounded-lg shadow hover:shadow-lg transition-shadow">
                      <div className="mb-4">
                        <div className="text-sm text-gray-600 font-medium mb-2">Вопрос</div>
                        <div className="text-gray-900 font-medium text-lg">{card.question}</div>
                      </div>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                        <div>
                          <div className="text-sm text-green-600 font-medium mb-2">
                            Правильные ответы {card.is_multiple ? '(несколько)' : '(один)'}
                          </div>
                          <ul className="list-disc list-inside space-y-1">
                            {card.correct_answers.map((ans, idx) => (
                              <li key={idx} className="text-gray-900">{ans}</li>
                            ))}
                          </ul>
                        </div>
                        <div>
                          <div className="text-sm text-red-600 font-medium mb-2">Неправильные ответы</div>
                          <ul className="list-disc list-inside space-y-1">
                            {card.wrong_answers.map((ans, idx) => (
                              <li key={idx} className="text-gray-700">{ans}</li>
                            ))}
                          </ul>
                        </div>
                      </div>
                      <div className="flex justify-end">
                        <button
                          onClick={() => handleDeleteQuizCard(card.id)}
                          className="px-4 py-2 bg-red-100 text-red-700 rounded hover:bg-red-200 font-medium"
                        >
                          Удалить
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </>
          )}
        </div>
      </main>

      {/* Add Card Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-lg shadow-xl max-w-2xl w-full mx-4">
            <h3 className="text-xl font-bold mb-4 text-gray-900">Добавить новую карточку</h3>
            <form onSubmit={handleAddCard}>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-900 mb-1">
                  Вопрос (лицевая сторона)
                </label>
                <textarea
                  required
                  value={newFront}
                  onChange={(e) => setNewFront(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md text-gray-900 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  rows={3}
                  placeholder="Введите вопрос..."
                />
              </div>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-900 mb-1">
                  Ответ (обратная сторона)
                </label>
                <textarea
                  required
                  value={newBack}
                  onChange={(e) => setNewBack(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md text-gray-900 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  rows={3}
                  placeholder="Введите ответ..."
                />
              </div>
              <div className="flex space-x-2">
                <button
                  type="button"
                  onClick={() => {
                    setShowAddModal(false);
                    setNewFront('');
                    setNewBack('');
                  }}
                  className="flex-1 px-4 py-2 bg-gray-200 text-gray-900 rounded-md hover:bg-gray-300 font-medium"
                >
                  Отмена
                </button>
                <button
                  type="submit"
                  className="flex-1 px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 font-medium"
                >
                  Добавить
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Edit Card Modal */}
      {showEditModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-lg shadow-xl max-w-2xl w-full mx-4">
            <h3 className="text-xl font-bold mb-4 text-gray-900">Редактировать карточку</h3>
            <form onSubmit={handleEditCard}>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-900 mb-1">
                  Вопрос (лицевая сторона)
                </label>
                <textarea
                  required
                  value={newFront}
                  onChange={(e) => setNewFront(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md text-gray-900 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  rows={3}
                />
              </div>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-900 mb-1">
                  Ответ (обратная сторона)
                </label>
                <textarea
                  required
                  value={newBack}
                  onChange={(e) => setNewBack(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md text-gray-900 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  rows={3}
                />
              </div>
              <div className="flex space-x-2">
                <button
                  type="button"
                  onClick={() => {
                    setShowEditModal(false);
                    setEditingCard(null);
                    setNewFront('');
                    setNewBack('');
                  }}
                  className="flex-1 px-4 py-2 bg-gray-200 text-gray-900 rounded-md hover:bg-gray-300 font-medium"
                >
                  Отмена
                </button>
                <button
                  type="submit"
                  className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 font-medium"
                >
                  Сохранить
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Add Quiz Card Modal */}
      {showAddQuizModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 overflow-y-auto">
          <div className="bg-white p-6 rounded-lg shadow-xl max-w-3xl w-full mx-4 my-8">
            <h3 className="text-xl font-bold mb-4 text-gray-900">Добавить Quiz карточки</h3>

            {/* Mode Selection */}
            <div className="flex space-x-2 mb-6">
              <button
                type="button"
                onClick={() => setQuizCreationMode('manual')}
                className={`flex-1 px-4 py-3 rounded-lg font-medium transition-colors ${
                  quizCreationMode === 'manual'
                    ? 'bg-purple-600 text-white'
                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                }`}
              >
                Вручную
              </button>
              <button
                type="button"
                onClick={() => setQuizCreationMode('ai')}
                className={`flex-1 px-4 py-3 rounded-lg font-medium transition-colors ${
                  quizCreationMode === 'ai'
                    ? 'bg-purple-600 text-white'
                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                }`}
              >
                AI режим
              </button>
            </div>

            {/* Manual Mode Form */}
            {quizCreationMode === 'manual' && (
              <form onSubmit={handleAddQuizCard}>
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-900 mb-1">
                    Вопрос
                  </label>
                  <textarea
                    required
                    value={quizQuestion}
                    onChange={(e) => setQuizQuestion(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md text-gray-900 focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                    rows={3}
                    placeholder="Введите вопрос..."
                  />
                </div>

                <div className="mb-4">
                  <label className="flex items-center space-x-2 mb-2">
                    <input
                      type="checkbox"
                      checked={isMultiple}
                      onChange={(e) => setIsMultiple(e.target.checked)}
                      className="w-4 h-4 text-purple-600 border-gray-300 rounded focus:ring-purple-500"
                    />
                    <span className="text-sm font-medium text-gray-900">Несколько правильных ответов</span>
                  </label>
                </div>

                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-900 mb-2">
                    Правильные ответы
                  </label>
                  {correctAnswers.map((answer, idx) => (
                    <div key={idx} className="flex space-x-2 mb-2">
                      <input
                        type="text"
                        required
                        value={answer}
                        onChange={(e) => updateCorrectAnswer(idx, e.target.value)}
                        className="flex-1 px-3 py-2 border border-gray-300 rounded-md text-gray-900 focus:ring-2 focus:ring-green-500 focus:border-green-500"
                        placeholder={`Правильный ответ ${idx + 1}`}
                      />
                      {correctAnswers.length > 1 && (
                        <button
                          type="button"
                          onClick={() => removeCorrectAnswer(idx)}
                          className="px-3 py-2 bg-red-100 text-red-700 rounded hover:bg-red-200"
                        >
                          ✕
                        </button>
                      )}
                    </div>
                  ))}
                  {isMultiple && (
                    <button
                      type="button"
                      onClick={addCorrectAnswer}
                      className="text-sm text-green-600 hover:text-green-700 font-medium"
                    >
                      + Добавить правильный ответ
                    </button>
                  )}
                </div>

                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-900 mb-2">
                    Неправильные ответы (опционально)
                  </label>
                  <p className="text-xs text-gray-600 mb-2">
                    Оставьте пустым для автоматической генерации через ИИ или выберите колоду-источник
                  </p>
                  {wrongAnswers.map((answer, idx) => (
                    <div key={idx} className="mb-2">
                      <input
                        type="text"
                        value={answer}
                        onChange={(e) => updateWrongAnswer(idx, e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md text-gray-900 focus:ring-2 focus:ring-red-500 focus:border-red-500"
                        placeholder={`Неправильный ответ ${idx + 1}`}
                      />
                    </div>
                  ))}
                </div>

                <div className="mb-4">
                  <label className="flex items-center space-x-2 mb-2">
                    <input
                      type="checkbox"
                      checked={generateWithAI}
                      onChange={(e) => setGenerateWithAI(e.target.checked)}
                      className="w-4 h-4 text-purple-600 border-gray-300 rounded focus:ring-purple-500"
                    />
                    <span className="text-sm font-medium text-gray-900">Генерировать неправильные ответы при помощи ИИ</span>
                  </label>
                </div>

                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-900 mb-1">
                    Колода-источник для неправильных ответов (опционально)
                  </label>
                  <select
                    value={sourceDeckId || ''}
                    onChange={(e) => setSourceDeckId(e.target.value ? Number(e.target.value) : undefined)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md text-gray-900 focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                  >
                    <option value="">Не выбрано</option>
                    {allDecks.map((d) => (
                      <option key={d.id} value={d.id}>{d.name}</option>
                    ))}
                  </select>
                </div>

                <div className="flex space-x-2">
                  <button
                    type="button"
                    onClick={() => {
                      setShowAddQuizModal(false);
                      resetQuizForm();
                    }}
                    className="flex-1 px-4 py-2 bg-gray-200 text-gray-900 rounded-md hover:bg-gray-300 font-medium"
                  >
                    Отмена
                  </button>
                  <button
                    type="submit"
                    className="flex-1 px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700 font-medium"
                  >
                    Создать
                  </button>
                </div>
              </form>
            )}

            {/* AI Mode Form */}
            {quizCreationMode === 'ai' && (
              <form onSubmit={handleBulkGenerateQuizCards}>
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-900 mb-1">
                    Тема для генерации
                  </label>
                  <input
                    type="text"
                    required
                    value={aiTopic}
                    onChange={(e) => setAiTopic(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md text-gray-900 focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                    placeholder="Например: История России, Математика, Программирование на Python..."
                  />
                </div>

                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-900 mb-1">
                    Детали и инструкции для AI (опционально)
                  </label>
                  <textarea
                    value={aiDetails}
                    onChange={(e) => setAiDetails(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md text-gray-900 focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                    rows={4}
                    placeholder="Например: Сосредоточься на периоде 1917-1945 годов, включи вопросы о ключевых событиях и личностях, сделай вопросы средней сложности..."
                  />
                  <p className="text-xs text-gray-600 mt-1">
                    Укажите дополнительные требования: уровень сложности, конкретные темы, стиль вопросов и т.д.
                  </p>
                </div>

                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-900 mb-1">
                    Количество вопросов
                  </label>
                  <input
                    type="number"
                    required
                    min="1"
                    max="20"
                    value={aiCount}
                    onChange={(e) => setAiCount(Number(e.target.value))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md text-gray-900 focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                  />
                  <p className="text-xs text-gray-600 mt-1">
                    Рекомендуется: 5-10 вопросов за раз
                  </p>
                </div>

                <div className="flex space-x-2">
                  <button
                    type="button"
                    onClick={() => {
                      setShowAddQuizModal(false);
                      resetQuizForm();
                    }}
                    disabled={isGenerating}
                    className="flex-1 px-4 py-2 bg-gray-200 text-gray-900 rounded-md hover:bg-gray-300 font-medium disabled:opacity-50"
                  >
                    Отмена
                  </button>
                  <button
                    type="submit"
                    disabled={isGenerating}
                    className="flex-1 px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700 font-medium disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {isGenerating ? 'Генерация...' : 'Сгенерировать'}
                  </button>
                </div>
              </form>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
