export interface QuizCard {
  id: number;
  deck_id: number;
  source_deck_id?: number;
  question: string;
  correct_answers: string[];
  wrong_answers: string[];
  is_multiple: boolean;
  created_at: string;
  updated_at: string;
}

export interface QuizStudyCard {
  id: number;
  deck_id: number;
  question: string;
  options: string[];
  is_multiple: boolean;
  progress_id?: number;
  ease_factor: number;
  interval_days: number;
  repetitions: number;
  due_date: string;
}

export interface QuizAnswerResult {
  correct: boolean;
  correct_answers: string[];
  selected_answers: string[];
  explanation?: string;
}
