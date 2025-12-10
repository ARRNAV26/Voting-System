export interface User {
  id: number;
  username: string;
  email: string;
  is_active: boolean;
  created_at: string;
}

export interface Suggestion {
  id: number;
  title: string;
  description: string;
  category: string;
  status: string;
  author_id: number;
  vote_count: number;
  created_at: string;
  updated_at?: string;
  author: User;
}

export interface Vote {
  id: number;
  user_id: number;
  suggestion_id: number;
  is_upvote: boolean;
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
}

export interface LoginForm {
  username: string;
  password: string;
}

export interface RegisterForm {
  username: string;
  email: string;
  password: string;
}

export interface SuggestionForm {
  title: string;
  description: string;
  category: string;
}

export interface VoteForm {
  suggestion_id: number;
  is_upvote: boolean;
}

export interface WebSocketMessage {
  message: any;
  type: string;
  data: any;
}

export interface VoteUpdateMessage {
  suggestion_id: number;
  new_vote_count: number;
  user_vote?: boolean;
}

export interface SuggestionUpdateMessage {
  suggestion: Suggestion;
}

export interface CategoryStats {
  category: string;
  count: number;
} 