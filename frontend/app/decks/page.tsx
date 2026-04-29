'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { decksAPI } from '@/lib/api';
import { Deck } from '@/lib/types';

export default function DecksPage() {
  const router = useRouter();
  const [decks, setDecks] = useState<Deck[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newDeckName, setNewDeckName] = useState('');
  const [newDeckDescription, setNewDeckDescription] = useState('');

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      router.push('/login');
      return;
    }

    loadDecks();
  }, []);

  const loadDecks = async () => {
    try {
      const response = await decksAPI.getAll();
      setDecks(response.data);
    } catch (err) {
      console.error('Failed to load decks', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateDeck = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await decksAPI.create({ name: newDeckName, description: newDeckDescription });
      setShowCreateModal(false);
      setNewDeckName('');
      setNewDeckDescription('');
      loadDecks();
    } catch (err) {
      console.error('Failed to create deck', err);
    }
  };

  const handleDeleteDeck = async (id: number) => {
    if (!confirm('Вы уверены, что хотите удалить эту колоду?')) return;
    try {
      await decksAPI.delete(id);
      loadDecks();
    } catch (err) {
      console.error('Failed to delete deck', err);
    }
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
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-2xl font-bold text-gray-900">Мои колоды</h2>
            <button
              onClick={() => setShowCreateModal(true)}
              className="px-6 py-3 bg-blue-600 text-white rounded-md hover:bg-blue-700 font-medium shadow-sm"
            >
              Создать колоду
            </button>
          </div>

          {decks.length === 0 ? (
            <div className="text-center py-12 bg-white rounded-lg shadow">
              <p className="text-gray-600 text-lg">Пока нет колод. Создайте первую!</p>
            </div>
          ) : (
            <>
              {/* Кнопка "Учить всё" */}
              {decks.some(d => (d.due_cards_count || 0) > 0) && (
                <div className="mb-6 p-6 bg-gradient-to-r from-blue-600 to-blue-700 rounded-lg shadow-lg">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-white text-xl font-bold mb-1">
                        Готовы к изучению
                      </h3>
                      <p className="text-blue-100 text-sm">
                        {decks.reduce((sum, d) => sum + (d.due_cards_count || 0), 0)} карточек из всех колод
                      </p>
                    </div>
                    <a
                      href="/study/all"
                      className="px-8 py-3 bg-white text-blue-600 rounded-lg hover:bg-blue-50 font-bold text-lg shadow-md transition-all hover:scale-105"
                    >
                      Учить всё
                    </a>
                  </div>
                </div>
              )}

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {decks.map((deck) => {
                  const isQuizDeck = deck.name.startsWith('Quiz:');
                  const dueCount = deck.due_cards_count || 0;
                  const hasDueCards = dueCount > 0;

                  return (
                    <div
                      key={deck.id}
                      className={`p-6 rounded-lg shadow hover:shadow-lg transition-all ${
                        hasDueCards
                          ? 'border-2 border-blue-300 bg-gradient-to-br from-blue-50 to-white'
                          : isQuizDeck
                          ? 'bg-gradient-to-br from-purple-50 to-white border-2 border-purple-200'
                          : 'bg-white'
                      }`}
                    >
                      <div className="flex items-start justify-between mb-2">
                        <h3 className="text-xl font-bold text-gray-900 flex-1">{deck.name}</h3>
                        <div className="flex flex-col items-end gap-1">
                          {isQuizDeck && (
                            <span className="px-2 py-1 bg-purple-600 text-white text-xs font-bold rounded-full">
                              QUIZ
                            </span>
                          )}
                          {hasDueCards && (
                            <span className="px-3 py-1 bg-blue-600 text-white text-sm font-bold rounded-full">
                              {dueCount}
                            </span>
                          )}
                        </div>
                      </div>
                      <p className="text-gray-700 text-sm mb-4">{deck.description}</p>
                      <div className="flex justify-between text-sm mb-4">
                        <span className="text-gray-600 font-medium">
                          {deck.cards_count || 0} карточек
                        </span>
                        {hasDueCards ? (
                          <span className="text-blue-600 font-bold">
                            {dueCount} к изучению
                          </span>
                        ) : (
                          <span className="text-green-600 font-medium">
                            ✓ Всё изучено
                          </span>
                        )}
                      </div>
                      <div className="flex space-x-2">
                        <a
                          href={`/decks/${deck.id}`}
                          className="flex-1 text-center px-3 py-2 bg-gray-100 text-gray-900 rounded hover:bg-gray-200 font-medium"
                        >
                          Открыть
                        </a>
                        {hasDueCards && (
                          <a
                            href={`/study/${deck.id}`}
                            className={`flex-1 text-center px-3 py-2 text-white rounded font-bold shadow-sm ${
                              isQuizDeck
                                ? 'bg-purple-600 hover:bg-purple-700'
                                : 'bg-blue-600 hover:bg-blue-700'
                            }`}
                          >
                            Учить
                          </a>
                        )}
                        <button
                          onClick={() => handleDeleteDeck(deck.id)}
                          className="px-3 py-2 bg-red-100 text-red-700 rounded hover:bg-red-200 font-medium"
                        >
                          Удалить
                        </button>
                      </div>
                    </div>
                  );
                })}
              </div>
            </>
          )}
        </div>
      </main>

      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-lg shadow-xl max-w-md w-full">
            <h3 className="text-xl font-bold mb-4 text-gray-900">Создать новую колоду</h3>
            <form onSubmit={handleCreateDeck}>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-900 mb-1">
                  Название колоды
                </label>
                <input
                  type="text"
                  required
                  value={newDeckName}
                  onChange={(e) => setNewDeckName(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md text-gray-900 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-900 mb-1">
                  Описание (необязательно)
                </label>
                <textarea
                  value={newDeckDescription}
                  onChange={(e) => setNewDeckDescription(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md text-gray-900 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  rows={3}
                />
              </div>
              <div className="flex space-x-2">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="flex-1 px-4 py-2 bg-gray-200 text-gray-900 rounded-md hover:bg-gray-300 font-medium"
                >
                  Отмена
                </button>
                <button
                  type="submit"
                  className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 font-medium"
                >
                  Создать
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
