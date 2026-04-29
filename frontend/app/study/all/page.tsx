'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import api from '@/lib/api';
import { StudyCard } from '@/lib/types';

export default function StudyAllPage() {
  const router = useRouter();

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
      const response = await api.get('/study/all/next');
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
      await api.post(`/study/review?card_id=${card.id}`, { rating });
      loadNextCard();
    } catch (err) {
      console.error('Failed to submit review', err);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
        <div className="text-lg sm:text-xl text-gray-900 font-medium">Загрузка...</div>
      </div>
    );
  }

  if (noCards) {
    return (
      <div className="min-h-screen bg-gray-50">
        <nav className="bg-white shadow">
          <div className="max-w-7xl mx-auto px-3 sm:px-4 lg:px-8">
            <div className="flex justify-between h-14 sm:h-16">
              <div className="flex items-center">
                <h1 className="text-lg sm:text-xl font-bold text-gray-900">Anki Web</h1>
              </div>
            </div>
          </div>
        </nav>

        <main className="max-w-3xl mx-auto py-6 sm:py-12 px-4">
          <div className="bg-white p-6 sm:p-8 rounded-lg shadow-xl text-center">
            <div className="text-4xl sm:text-6xl mb-3 sm:mb-4">🎉</div>
            <h2 className="text-xl sm:text-2xl font-bold mb-3 sm:mb-4 text-gray-900">Все карточки изучены!</h2>
            <p className="text-base sm:text-lg text-gray-700 mb-4 sm:mb-6">
              Вы завершили все карточки из всех колод на сегодня. Отличная работа!
            </p>
            <a
              href="/decks"
              className="inline-block px-5 sm:px-6 py-2.5 sm:py-3 bg-blue-600 text-white rounded-md hover:bg-blue-700 font-medium text-sm sm:text-base"
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
      <nav className="bg-white shadow sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-3 sm:px-4 lg:px-8">
          <div className="flex justify-between h-14 sm:h-16">
            <div className="flex items-center space-x-2 sm:space-x-4">
              <h1 className="text-lg sm:text-xl font-bold text-gray-900">Anki Web</h1>
              <span className="px-2 sm:px-3 py-1 bg-blue-100 text-blue-800 text-xs sm:text-sm font-bold rounded-full">
                Учить всё
              </span>
            </div>
            <div className="flex items-center">
              <a href="/decks" className="text-sm sm:text-base text-gray-900 hover:text-blue-600 font-medium">
                Вернуться
              </a>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-3xl mx-auto py-4 sm:py-8 lg:py-12 px-3 sm:px-4">
        <div className="bg-white rounded-lg shadow-xl overflow-hidden">
          <div className="p-4 sm:p-6 lg:p-8">
            <div className="text-center mb-6 sm:mb-8">
              <div className="text-xs sm:text-sm text-gray-600 mb-2 font-medium">Вопрос</div>
              <div className="text-lg sm:text-xl lg:text-2xl font-medium text-gray-900 min-h-[80px] sm:min-h-[100px] flex items-center justify-center px-2">
                {card?.front}
              </div>
            </div>

            {showAnswer && (
              <div className="border-t pt-6 sm:pt-8 mb-6 sm:mb-8">
                <div className="text-center">
                  <div className="text-xs sm:text-sm text-gray-600 mb-2 font-medium">Ответ</div>
                  <div className="text-base sm:text-lg lg:text-xl text-gray-800 min-h-[80px] sm:min-h-[100px] flex items-center justify-center px-2">
                    {card?.back}
                  </div>
                </div>
              </div>
            )}

            {!showAnswer ? (
              <button
                onClick={() => setShowAnswer(true)}
                className="w-full py-3 sm:py-3.5 bg-blue-600 text-white rounded-md hover:bg-blue-700 text-base sm:text-lg font-medium shadow-sm active:scale-95 transition-transform"
              >
                Показать ответ
              </button>
            ) : (
              <div className="grid grid-cols-2 gap-2 sm:gap-3">
                <button
                  onClick={() => handleReview('again')}
                  className="py-3 sm:py-3.5 bg-red-100 text-red-800 rounded-md hover:bg-red-200 font-medium text-sm sm:text-base active:scale-95 transition-transform"
                >
                  <div>Снова</div>
                  <div className="text-xs text-red-600 mt-0.5 sm:mt-1">&lt;1 мин</div>
                </button>
                <button
                  onClick={() => handleReview('hard')}
                  className="py-3 sm:py-3.5 bg-orange-100 text-orange-800 rounded-md hover:bg-orange-200 font-medium text-sm sm:text-base active:scale-95 transition-transform"
                >
                  <div>Сложно</div>
                  <div className="text-xs text-orange-600 mt-0.5 sm:mt-1">~10 мин</div>
                </button>
                <button
                  onClick={() => handleReview('good')}
                  className="py-3 sm:py-3.5 bg-green-100 text-green-800 rounded-md hover:bg-green-200 font-medium text-sm sm:text-base active:scale-95 transition-transform"
                >
                  <div>Хорошо</div>
                  <div className="text-xs text-green-600 mt-0.5 sm:mt-1">
                    {card?.state === 'new' || card?.state === 'learning' ? '1 день' : `${Math.round((card?.interval_days || 1) * (card?.ease_factor || 2.5))} дней`}
                  </div>
                </button>
                <button
                  onClick={() => handleReview('easy')}
                  className="py-3 sm:py-3.5 bg-blue-100 text-blue-800 rounded-md hover:bg-blue-200 font-medium text-sm sm:text-base active:scale-95 transition-transform"
                >
                  <div>Легко</div>
                  <div className="text-xs text-blue-600 mt-0.5 sm:mt-1">
                    {card?.state === 'new' || card?.state === 'learning' ? '4 дня' : `${Math.round((card?.interval_days || 1) * (card?.ease_factor || 2.5) * 1.3)} дней`}
                  </div>
                </button>
              </div>
            )}
          </div>

          <div className="bg-gray-50 px-4 sm:px-6 lg:px-8 py-3 sm:py-4 text-xs sm:text-sm text-gray-700 border-t">
            <div className="flex flex-col sm:flex-row sm:justify-between gap-2 sm:gap-0 font-medium">
              <span>Повторений: {card?.repetitions || 0}</span>
              <span>Интервал: {card?.interval_days || 0} дней</span>
              <span className="text-blue-600">
                {card?.state === 'new' ? 'Новая' : card?.state === 'learning' ? 'Обучение' : card?.state === 'review' ? 'Повторение' : 'Переобучение'}
              </span>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
