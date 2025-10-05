import { useState } from 'react';
import { GenerationHistory, FeedbackItem } from '@/types';

export const useDataState = () => {
  const [generationHistory, setGenerationHistory] = useState<GenerationHistory[]>([
    {
      id: 1,
      date: '2025-10-03',
      time: '14:30',
      platform: 'Instagram',
      tone: 'Energetic',
      adText: 'Try our new fitness app!',
      outputs: 'Text, Poster, Video',
      status: 'Completed'
    },
    {
      id: 2,
      date: '2025-10-04',
      time: '09:15',
      platform: 'LinkedIn',
      tone: 'Professional',
      adText: 'Grow your business with AI',
      outputs: 'Text, Poster',
      status: 'Completed'
    },
    {
      id: 3,
      date: '2025-10-04',
      time: '16:45',
      platform: 'TikTok',
      tone: 'Fun',
      adText: 'Dance with our new app!',
      outputs: 'Text, Video',
      status: 'Completed'
    }
  ]);

  const [feedbackList, setFeedbackList] = useState<FeedbackItem[]>([
    {
      id: 1,
      email: 'user1@example.com',
      message: 'Amazing platform! Generated ads look professional.',
      rating: 5,
      action: 'Copied Text',
      date: '2025-10-03',
      platform: 'Instagram'
    },
    {
      id: 2,
      email: 'creator@startup.io',
      message: 'Love the video quality. Could use more templates.',
      rating: 4,
      action: 'Downloaded Video',
      date: '2025-10-04',
      platform: 'TikTok'
    },
    {
      id: 3,
      email: 'marketing@company.com',
      message: 'Saved us thousands! Highly recommend.',
      rating: 5,
      action: 'Downloaded Poster',
      date: '2025-10-04',
      platform: 'LinkedIn'
    }
  ]);

  return {
    generationHistory,
    setGenerationHistory,
    feedbackList,
    setFeedbackList
  };
};
