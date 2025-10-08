import { useCallback } from 'react';
import { useAppState } from './useAppState';
import { useApiData } from './useApiData';

export const useFeedbackHandler = (appState: ReturnType<typeof useAppState>, apiData: ReturnType<typeof useApiData>) => {
  const handleActionClick = useCallback(async (type: string) => {
    // Handle download actions directly first
    if (type === 'download-poster' && appState.result?.poster_url) {
      try {
        console.log('📥 Starting poster download...');

        // Construct the full backend URL for downloads
        const backendUrl = 'http://localhost:8000'; // Backend runs on port 8000
        const downloadUrl = appState.result.poster_url.startsWith('http')
          ? appState.result.poster_url
          : `${backendUrl}${appState.result.poster_url}`;

        console.log('📥 Download URL:', downloadUrl);

        // Fetch the file from the download endpoint
        const response = await fetch(downloadUrl);

        if (!response.ok) {
          console.error('❌ Download failed:', response.status, response.statusText);
          alert(`Download failed: ${response.status} ${response.statusText}`);
          return;
        }

        // Get the filename from the URL
        const urlParts = appState.result.poster_url.split('/');
        const filename = urlParts[urlParts.length - 1] || 'poster.png';

        // Create blob from response
        const blob = await response.blob();
        console.log(`📥 Downloaded ${blob.size} bytes`);

        // Create download link
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);

        console.log('✅ Poster download completed');

        // Show feedback modal after download
        appState.setFeedbackType('download-poster');
        appState.setShowFeedbackModal(true);
      } catch (error) {
        console.error('❌ Download error:', error);
        alert('Download failed. Please check the console for details.');
      }
      return;
    }

    if (type === 'download-video') {
      // Show feedback modal for video download
      appState.setFeedbackType('download-video');
      appState.setShowFeedbackModal(true);
      return;
    }

    // For other actions, just show feedback modal
    appState.setFeedbackType(type as any);
    appState.setShowFeedbackModal(true);
  }, [appState]);

  const submitFeedback = useCallback(async () => {
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
      id: 0, // Will be set by backend
      email: appState.feedback.email,
      message: appState.feedback.message,
      rating: appState.feedback.rating,
      action: actionMap[appState.feedbackType || ''] || 'Unknown Action',
      date: new Date().toISOString().split('T')[0],
      platform: appState.formData.platform
    };

    // Save feedback for all users (not just admins)
    try {
      await apiData.addFeedback(newFeedback);
      alert('Thank you for your feedback!');
      console.log('✅ Feedback saved to database');
    } catch (error) {
      console.error('❌ Failed to save feedback:', error);
      alert('Unable to record feedback. Please try again.');
      return; // Don't close modal if save failed
    }

    appState.setShowFeedbackModal(false);
    appState.setFeedback({ email: '', message: '', rating: 5 });
  }, [appState, apiData]);

  return { handleActionClick, submitFeedback };
};
