'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { statsAPI } from '@/lib/api';
import { DashboardStats } from '@/lib/types';

export default function DashboardPage() {
  const router = useRouter();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      router.push('/login');
      return;
    }

    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      const response = await statsAPI.getDashboard();
      setStats(response.data);
    } catch (err) {
      console.error('Failed to load stats', err);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    router.push('/login');
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
              <a href="/decks" className="text-gray-900 hover:text-blue-600 font-medium">
                Колоды
              </a>
              <button
                onClick={handleLogout}
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
          <h2 className="text-2xl font-bold mb-6 text-gray-900">Панель управления</h2>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <div className="bg-white p-6 rounded-lg shadow">
              <div className="text-sm text-gray-600 font-medium">Всего колод</div>
              <div className="text-3xl font-bold text-gray-900">{stats?.total_decks || 0}</div>
            </div>
            <div className="bg-white p-6 rounded-lg shadow">
              <div className="text-sm text-gray-600 font-medium">Всего карточек</div>
              <div className="text-3xl font-bold text-gray-900">{stats?.total_cards || 0}</div>
            </div>
            <div className="bg-white p-6 rounded-lg shadow">
              <div className="text-sm text-gray-600 font-medium">К изучению сегодня</div>
              <div className="text-3xl font-bold text-blue-600">
                {stats?.due_today || 0}
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-white p-6 rounded-lg shadow">
              <div className="text-sm text-gray-600 font-medium">Изучено сегодня</div>
              <div className="text-3xl font-bold text-gray-900">{stats?.studied_today || 0}</div>
            </div>
            <div className="bg-white p-6 rounded-lg shadow">
              <div className="text-sm text-gray-600 font-medium">Серия дней</div>
              <div className="text-3xl font-bold text-green-600">
                {stats?.streak_days || 0} дней
              </div>
            </div>
            <div className="bg-white p-6 rounded-lg shadow">
              <div className="text-sm text-gray-600 font-medium">Точность</div>
              <div className="text-3xl font-bold text-gray-900">
                {stats?.accuracy_percent?.toFixed(1) || 0}%
              </div>
            </div>
          </div>

          <div className="mt-8">
            <a
              href="/decks"
              className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700"
            >
              Перейти к колодам
            </a>
          </div>
        </div>
      </main>
    </div>
  );
}
