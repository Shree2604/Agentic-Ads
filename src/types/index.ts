export interface FormData {
  adText: string;
  tone: string;
  platform: string;
  outputs: string[];
  logoPosition: string;
  logo?: File;
}

export interface GenerationResult {
  rewrittenText: string;
  posterUrl: string;
  videoUrl: string;
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
