export interface FormData {
  adText: string;
  tone: string;
  platform: string;
  outputs: string[];
  logo?: File;
  brandGuidelines?: string;
}

export interface GenerationResult {
  rewrittenText: string;
  posterUrl: string;
  poster_url?: string; // For base64 encoded poster image
  videoUrl: string;
  qualityScores?: Record<string, number>;
  validationFeedback?: Record<string, string>;
}

export interface Feedback {
  email: string;
  message: string;
  rating: number;
}

export interface AdminCredentials {
  username: string;
  password: string;
}

export interface GenerationHistory {
  id: number;
  date: string;
  time: string;
  platform: string;
  tone: string;
  adText: string;
  outputs: string;
  status: string;
}

export interface FeedbackItem {
  id: number;
  email: string;
  message: string;
  rating: number;
  action: string;
  date: string;
  platform: string;
}

export interface OutputType {
  id: string;
  label: string;
  icon: any;
}

export type ViewType = 'welcome' | 'app' | 'admin';
export type FeedbackType = 'copy' | 'download-poster' | 'download-video' | null;
export type Tone = 'professional' | 'casual' | 'energetic' | 'fun' | 'witty';
export type Platform = 'Instagram' | 'LinkedIn' | 'Twitter' | 'YouTube';
