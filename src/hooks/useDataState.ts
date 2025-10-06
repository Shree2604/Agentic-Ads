import { useState } from 'react';
import { GenerationHistory, FeedbackItem } from '@/types';

export const useDataState = () => {
  const [generationHistory, setGenerationHistory] = useState<GenerationHistory[]>([]);
  const [feedbackList, setFeedbackList] = useState<FeedbackItem[]>([]);

  return {
    generationHistory,
    setGenerationHistory,
    feedbackList,
    setFeedbackList
  };
};
