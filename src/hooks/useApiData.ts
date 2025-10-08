import { useState, useEffect, useCallback } from 'react';
import { GenerationHistory, FeedbackItem } from '@/types';
import { API_BASE_URL } from '@/config/api';

export const useApiData = (token: string | null) => {
  const [generationHistory, setGenerationHistory] = useState<GenerationHistory[]>([]);
  const [feedbackList, setFeedbackList] = useState<FeedbackItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const publicFetch = useCallback(async (endpoint: string, options: RequestInit = {}) => {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, options);

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response;
  }, []);

  const authorizedFetch = useCallback(async (endpoint: string, options: RequestInit = {}) => {
    if (!token) {
      throw new Error('Unauthorized');
    }

    const headers: HeadersInit = {
      ...(options.headers || {}),
      Authorization: `Bearer ${token}`
    };

    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers
    });

    if (response.status === 401) {
      setError('Unauthorized');
      throw new Error('Unauthorized');
    }

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response;
  }, [token]);

  // Fetch generation history (public endpoint)
  const fetchGenerationHistory = useCallback(async () => {
    try {
      const response = await publicFetch('/generation-history');
      const data = await response.json();
      setGenerationHistory(data);
    } catch (err) {
      console.error('Error fetching generation history:', err);
      if ((err as Error).message !== 'Unauthorized') {
        setError('Failed to fetch generation history');
      }
      throw err;
    }
  }, [publicFetch]);

  // Fetch feedback list (public endpoint)
  const fetchFeedbackList = useCallback(async () => {
    try {
      const response = await publicFetch('/feedback');
      const data = await response.json();
      setFeedbackList(data);
    } catch (err) {
      console.error('Error fetching feedback list:', err);
      if ((err as Error).message !== 'Unauthorized') {
        setError('Failed to fetch feedback list');
      }
      throw err;
    }
  }, [publicFetch]);

  // Add new generation history (public endpoint)
  const addGenerationHistory = async (generation: Omit<GenerationHistory, 'id'>) => {
    try {
      const newId = Math.max(...generationHistory.map(g => g.id), 0) + 1;
      const generationWithId = { ...generation, id: newId };
      await publicFetch('/generation-history', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(generationWithId),
      });

      setGenerationHistory(prev => [...prev, generationWithId]);
      return generationWithId;
    } catch (err) {
      console.error('Error adding generation history:', err);
      throw err;
    }
  };

  // Add new feedback (public endpoint)
  const addFeedback = async (feedback: Omit<FeedbackItem, 'id'>) => {
    try {
      const newId = Math.max(...feedbackList.map(f => f.id), 0) + 1;
      const feedbackWithId = { ...feedback, id: newId };

      await publicFetch('/feedback', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(feedbackWithId),
      });

      setFeedbackList(prev => [...prev, feedbackWithId]);
      return feedbackWithId;
    } catch (err) {
      console.error('Error adding feedback:', err);
      throw err;
    }
  };

  // Fetch all data on mount (public endpoints don't need token)
  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError(null);

      try {
        await Promise.all([fetchGenerationHistory(), fetchFeedbackList()]);
      } catch (err) {
        // Error is already set in individual functions
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [fetchGenerationHistory, fetchFeedbackList]);

  // Refresh data (public endpoints don't need token)
  const refreshData = async () => {
    setLoading(true);
    setError(null);

    try {
      await Promise.all([fetchGenerationHistory(), fetchFeedbackList()]);
    } catch (err) {
      // Error is already set in individual functions
    } finally {
      setLoading(false);
    }
  };

  return {
    generationHistory,
    feedbackList,
    loading,
    error,
    addGenerationHistory,
    addFeedback,
    refreshData,
  };
};
