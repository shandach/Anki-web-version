export interface User {
  id: number;
  email: string;
  name: string;
  created_at: string;
}

export interface Deck {
  id: number;
  user_id: number;
  name: string;
  description?: string;
  created_at: string;
  updated_at: string;
  cards_count?: number;
  due_cards_count?: number;
}

export interface Card {
  id: number;
  deck_id: number;
  front: string;
  back: string;
  created_at: string;
  updated_at: string;
}

export interface StudyCard {
  id: number;
  deck_id: number;
  front: string;
  back: string;
  progress_id?: number;
  ease_factor: number;
  interval_days: number;
  repetitions: number;
  due_date: string;
  state?: string;
  learning_step?: number;
}

export interface DashboardStats {
  total_decks: number;
  total_cards: number;
  due_today: number;
  studied_today: number;
  streak_days: number;
  accuracy_percent: number;
}
