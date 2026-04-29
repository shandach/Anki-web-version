'use client';

import { useEffect, useState } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { quizAPI } from '@/lib/quiz-api';
import { QuizStudyCard, QuizAnswerResult } from '@/lib/quiz-types';

export default function QuizStudyPage() {
  const router = useRouter();
  const params = useParams();
  const deckId = Number(params.deckId);

  const [card, setCard] = useState<QuizStudyCard | null>(null);
  const [selectedAnswers, setSelectedAnswers] = useState<string[]>([]);
  const [result, setResult] = useState<QuizAnswerResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [showResult, setShowResult] = useState(false);
  const [currentCardIndex, setCurrentCardIndex] = useState(1);
  const [totalCards, setTotalCards] = useState(0);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      router.push('/login');
      return;
    }

    loadTotalCards();
    loadNextCard();
  }, []);

  const loadTotalCards = async () => {
    try {
      const response = await quizAPI.getAll(deckId);
      setTotalCards(response.data.length);
    } catch (err) {
      console.error('Failed to load total cards', err);
    }
  };

  const loadNextCard = async () => {
    try {
      setLoading(true);
      setShowResult(false);
      setResult(null);
      setSelectedAnswers([]);
      const response = await quizAPI.getNext(deckId);
      setCard(response.data);
    } catch (err: any) {
      if (err.response?.status === 404) {
        alert('Нет карточек для изучения');
        router.push(`/decks/${deckId}`);
      } else {
        console.error('Failed to load card', err);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleOptionClick = (option: string) => {
    if (showResult) return;

    if (card?.is_multiple) {
      if (selectedAnswers.includes(option)) {
        setSelectedAnswers(selectedAnswers.filter(a => a !== option));
      } else {
        setSelectedAnswers([...selectedAnswers, option]);
      }
    } else {
      setSelectedAnswers([option]);
    }
  };

  const handleSubmit = async () => {
    if (!card || selectedAnswers.length === 0) return;

    try {
      const response = await quizAPI.submitAnswer(card.id, selectedAnswers);
      setResult(response.data);
      setShowResult(true);
    } catch (err) {
      console.error('Failed to submit answer', err);
    }
  };

  const handleNext = () => {
    setCurrentCardIndex(prev => prev + 1);
    loadNextCard();
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-xl text-gray-900 font-medium">Загрузка...</div>
      </div>
    );
  }

  if (!card) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-xl text-gray-900 font-medium">Нет карточек для изучения</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-bold text-gray-900">Quiz режим</h1>
            </div>
            <div className="flex items-center space-x-4">
              <a
                href={`/decks/${deckId}`}
                className="text-gray-900 hover:text-blue-600 font-medium"
              >
                Вернуться к колоде
              </a>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-4xl mx-auto py-8 px-4">
        {/* Progress Counter */}
        <div className="bg-purple-100 p-4 rounded-lg shadow mb-4">
          <div className="text-center">
            <span className="text-lg font-bold text-purple-900">
              Вопрос {currentCardIndex} из {totalCards}
            </span>
          </div>
        </div>

        {/* Progress Info */}
        <div className="bg-white p-4 rounded-lg shadow mb-6">
          <div className="flex justify-between items-center text-sm text-gray-600">
            <div>
              <span className="font-medium">Повторений: {card.repetitions}</span>
              <span className="mx-2">•</span>
              <span className="font-medium">Интервал: {card.interval_days} дней</span>
            </div>
            <div>
              <span className="font-medium">Коэффициент: {card.ease_factor.toFixed(2)}</span>
            </div>
          </div>
        </div>

        {/* Question Card */}
        <div className="bg-white p-8 rounded-lg shadow-lg mb-6">
          <div className="text-center mb-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              {card.question}
            </h2>
            {card.is_multiple && (
              <p className="text-sm text-purple-600 font-medium">
                Выберите все правильные ответы
              </p>
            )}
          </div>

          {/* Options */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
            {card.options.map((option, idx) => {
              const isSelected = selectedAnswers.includes(option);
              const isCorrect = result?.correct_answers.includes(option);
              const isWrong = showResult && isSelected && !isCorrect;

              let bgColor = 'bg-white hover:bg-gray-50';
              let borderColor = 'border-gray-300';
              let textColor = 'text-gray-900';

              if (showResult) {
                if (isCorrect) {
                  bgColor = 'bg-green-50';
                  borderColor = 'border-green-500';
                  textColor = 'text-green-900';
                } else if (isWrong) {
                  bgColor = 'bg-red-50';
                  borderColor = 'border-red-500';
                  textColor = 'text-red-900';
                }
              } else if (isSelected) {
                bgColor = 'bg-purple-50';
                borderColor = 'border-purple-500';
                textColor = 'text-purple-900';
              }

              return (
                <button
                  key={idx}
                  onClick={() => handleOptionClick(option)}
                  disabled={showResult}
                  className={`p-6 rounded-lg border-2 ${bgColor} ${borderColor} transition-all ${
                    !showResult ? 'cursor-pointer' : 'cursor-default'
                  }`}
                >
                  <div className="flex items-center space-x-3">
                    {card.is_multiple ? (
                      <div className={`w-5 h-5 border-2 rounded ${
                        isSelected ? 'bg-purple-600 border-purple-600' : 'border-gray-400'
                      } flex items-center justify-center`}>
                        {isSelected && (
                          <svg className="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                          </svg>
                        )}
                      </div>
                    ) : (
                      <div className={`w-5 h-5 border-2 rounded-full ${
                        isSelected ? 'border-purple-600' : 'border-gray-400'
                      } flex items-center justify-center`}>
                        {isSelected && (
                          <div className="w-3 h-3 bg-purple-600 rounded-full"></div>
                        )}
                      </div>
                    )}
                    <span className={`text-left font-medium ${textColor}`}>
                      {option}
                    </span>
                  </div>
                </button>
              );
            })}
          </div>

          {/* Result Message */}
          {showResult && result && (
            <div className={`p-4 rounded-lg mb-6 ${
              result.correct ? 'bg-green-100 border border-green-300' : 'bg-red-100 border border-red-300'
            }`}>
              <p className={`text-center font-bold text-lg ${
                result.correct ? 'text-green-900' : 'text-red-900'
              }`}>
                {result.correct ? '✓ Правильно!' : '✗ Неправильно'}
              </p>
              {!result.correct && (
                <p className="text-center text-gray-900 mt-2">
                  Правильные ответы: {result.correct_answers.join(', ')}
                </p>
              )}
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex justify-center">
            {!showResult ? (
              <button
                onClick={handleSubmit}
                disabled={selectedAnswers.length === 0}
                className={`px-8 py-3 rounded-lg font-medium text-white ${
                  selectedAnswers.length === 0
                    ? 'bg-gray-400 cursor-not-allowed'
                    : 'bg-purple-600 hover:bg-purple-700'
                }`}
              >
                Проверить
              </button>
            ) : (
              <button
                onClick={handleNext}
                className="px-8 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium"
              >
                Следующая карточка
              </button>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
