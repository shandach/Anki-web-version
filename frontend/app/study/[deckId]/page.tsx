'use client';

import { useEffect, useState } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { studyAPI } from '@/lib/api';
import { StudyCard } from '@/lib/types';

export default function StudyPage() {
  const router = useRouter();
  const params = useParams();
  const deckId = Number(params.deckId);

  const [card, setCard] = useState<StudyCard | null>(null);
  const [showAnswer, setShowAnswer] = useState(false);
  const [loading, setLoading] = useState(true);
  const [noCards, setNoCards] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      router.push('/login');
      return;
    }

    loadNextCard();
  }, []);

  const loadNextCard = async () => {
    setLoading(true);
    setShowAnswer(false);
    try {
      const response = await studyAPI.getNext(deckId);
      setCard(response.data);
      setNoCards(false);
    } catch (err: any) {
      if (err.response?.status === 404) {
        setNoCards(true);
      }
      console.error('Failed to load card', err);
    } finally {
      setLoading(false);
    }
  };

  const handleReview = async (rating: string) => {
    if (!card) return;

    try {
      await studyAPI.review(card.id, rating);
      loadNextCard();
    } catch (err) {
      console.error('Failed to submit review', err);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-xl text-gray-900 font-medium">Загрузка...</div>
      </div>
    );
  }

  if (noCards) {
    return (
      <div className="min-h-screen bg-gray-50">
        <nav className="bg-white shadow">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between h-16">
              <div className="flex items-center">
                <h1 className="text-xl font-bold text-gray-900">Anki Web</h1>
              </div>
            </div>
          </div>
        </nav>

        <main className="max-w-3xl mx-auto py-12 px-4">
          <div className="bg-white p-8 rounded-lg shadow-xl text-center">
            <h2 className="text-2xl font-bold mb-4 text-gray-900">Нет карточек для изучения!</h2>
            <p className="text-gray-700 mb-6 text-lg">
              Вы завершили все карточки на сегодня. Отличная работа!
            </p>
            <a
              href="/decks"
              className="inline-block px-6 py-3 bg-blue-600 text-white rounded-md hover:bg-blue-700 font-medium"
            >
              Вернуться к колодам
            </a>
          </div>
        </main>
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
            <div className="flex items-center">
              <a href="/decks" className="text-gray-900 hover:text-blue-600 font-medium">
                Вернуться к колодам
              </a>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-3xl mx-auto py-12 px-4">
        <div className="bg-white rounded-lg shadow-xl overflow-hidden">
          <div className="p-8">
            <div className="text-center mb-8">
              <div className="text-sm text-gray-600 mb-2 font-medium">Вопрос</div>
              <div className="text-2xl font-medium text-gray-900 min-h-[100px] flex items-center justify-center">
                {card?.front}
              </div>
            </div>

            {showAnswer && (
              <div className="border-t pt-8 mb-8">
                <div className="text-center">
                  <div className="text-sm text-gray-600 mb-2 font-medium">Ответ</div>
                  <div className="text-xl text-gray-800 min-h-[100px] flex items-center justify-center">
                    {card?.back}
                  </div>
                </div>
              </div>
            )}

            {!showAnswer ? (
              <button
                onClick={() => setShowAnswer(true)}
                className="w-full py-3 bg-blue-600 text-white rounded-md hover:bg-blue-700 text-lg font-medium shadow-sm"
              >
                Показать ответ
              </button>
            ) : (
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                <button
                  onClick={() => handleReview('again')}
                  className="py-3 bg-red-100 text-red-800 rounded-md hover:bg-red-200 font-medium"
                >
                  Снова
                  <div className="text-xs text-red-600 mt-1">&lt;1 мин</div>
                </button>
                <button
                  onClick={() => handleReview('hard')}
                  className="py-3 bg-orange-100 text-orange-800 rounded-md hover:bg-orange-200 font-medium"
                >
                  Сложно
                  <div className="text-xs text-orange-600 mt-1">~10 мин</div>
                </button>
                <button
                  onClick={() => handleReview('good')}
                  className="py-3 bg-green-100 text-green-800 rounded-md hover:bg-green-200 font-medium"
                >
                  Хорошо
                  <div className="text-xs text-green-600 mt-1">
                    {card?.state === 'new' || card?.state === 'learning' ? '1 день' : `${Math.round((card?.interval_days || 1) * (card?.ease_factor || 2.5))} дней`}
                  </div>
                </button>
                <button
                  onClick={() => handleReview('easy')}
                  className="py-3 bg-blue-100 text-blue-800 rounded-md hover:bg-blue-200 font-medium"
                >
                  Легко
                  <div className="text-xs text-blue-600 mt-1">
                    {card?.state === 'new' || card?.state === 'learning' ? '4 дня' : `${Math.round((card?.interval_days || 1) * (card?.ease_factor || 2.5) * 1.3)} дней`}
                  </div>
                </button>
              </div>
            )}
          </div>

          <div className="bg-gray-50 px-8 py-4 text-sm text-gray-700 border-t">
            <div className="flex justify-between font-medium">
              <span>Повторений: {card?.repetitions || 0}</span>
              <span>Интервал: {card?.interval_days || 0} дней</span>
              <span className="text-blue-600">
                Состояние: {card?.state === 'new' ? 'Новая' : card?.state === 'learning' ? 'Обучение' : card?.state === 'review' ? 'Повторение' : 'Переобучение'}
              </span>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
