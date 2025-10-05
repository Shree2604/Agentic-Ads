import { useCallback } from 'react';
import { useAppState } from './useAppState';
import { useDataState } from './useDataState';

export const useFeedbackHandler = (appState: ReturnType<typeof useAppState>, dataState: ReturnType<typeof useDataState>) => {
  const handleActionClick = useCallback((type: string) => {
    appState.setFeedbackType(type as any);
    appState.setShowFeedbackModal(true);
  }, [appState]);

  const submitFeedback = useCallback(() => {
    if (!appState.feedback.email || !appState.feedback.message) {
      alert('Please fill in all fields');
      return;
    }

    const actionMap: Record<string, string> = {
      'copy': 'Copied Text',
      'download-poster': 'Downloaded Poster',
      'download-video': 'Downloaded Video'
    };

    const newFeedback = {
      id: dataState.feedbackList.length + 1,
      email: appState.feedback.email,
      message: appState.feedback.message,
      rating: appState.feedback.rating,
      action: actionMap[appState.feedbackType || ''] || 'Unknown Action',
      date: new Date().toISOString().split('T')[0],
      platform: appState.formData.platform
    };

    dataState.setFeedbackList([newFeedback, ...dataState.feedbackList]);

    // Handle the actual action
    if (appState.feedbackType === 'copy' && appState.result) {
      navigator.clipboard.writeText(appState.result.rewrittenText);
      alert('Text copied to clipboard!');
    } else {
      alert(`${actionMap[appState.feedbackType || '']} successfully!`);
    }

    appState.setShowFeedbackModal(false);
    appState.setFeedback({ email: '', message: '', rating: 5 });
  }, [appState, dataState]);

  return { handleActionClick, submitFeedback };
};
