import { useCallback } from 'react';
import { API_BASE_URL } from '@/config/api';
import { useAppState } from './useAppState';
import { useApiData } from './useApiData';

export const useFeedbackHandler = (appState: ReturnType<typeof useAppState>, apiData: ReturnType<typeof useApiData>) => {
  const normalizedApiBase = (API_BASE_URL || '').replace(/\/+$/, '') || 'http://localhost:8000/api';
  const backendBaseUrl = normalizedApiBase.replace(/\/api(?:\/.*)?$/i, '') || 'http://localhost:8000';

  const resolveBackendUrl = useCallback((path?: string | null) => {
    if (!path) {
      return undefined;
    }

    if (/^(https?:)?\/\//i.test(path) || path.startsWith('data:')) {
      return path;
    }

    const normalizedPath = path.startsWith('/') ? path : `/${path}`;
    return `${backendBaseUrl}${normalizedPath}`;
  }, [backendBaseUrl]);

  const downloadAsset = useCallback(async (downloadUrl: string, filename: string) => {
    const response = await fetch(downloadUrl);

    if (!response.ok) {
      throw new Error(`Download failed: ${response.status} ${response.statusText}`);
    }

    const blob = await response.blob();
    console.log(`📥 Downloaded ${blob.size} bytes from ${downloadUrl}`);

    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  }, []);

  const deriveFilename = (url: string, fallback: string) => {
    try {
      const parsed = new URL(url, window.location.href);
      const segments = parsed.pathname.split('/').filter(Boolean);
      if (segments.length > 0) {
        return segments[segments.length - 1];
      }
    } catch (error) {
      console.warn('⚠️ Unable to derive filename from URL:', url, error);
    }

    const sanitized = url.split('/').filter(Boolean).pop();
    return sanitized || fallback;
  };

  const handleActionClick = useCallback(async (type: string) => {
    // Handle download actions directly first
    if (type === 'download-poster' && appState.result?.poster_url) {
      try {
        console.log('📥 Starting poster download...');
        const downloadUrl = resolveBackendUrl(appState.result.poster_url);

        if (!downloadUrl) {
          alert('Poster file is not available yet. Please try again shortly.');
          return;
        }

        const filename = deriveFilename(downloadUrl, 'generated-poster.png');
        await downloadAsset(downloadUrl, filename);

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
      if (!appState.result?.videoUrl) {
        alert('Video file is not available yet. Please try again once the GIF is ready.');
        return;
      }

      try {
        console.log('📥 Starting video download...');
        const downloadUrl = resolveBackendUrl(appState.result.videoUrl);

        if (!downloadUrl) {
          alert('Video file is not available yet. Please try again once the GIF is ready.');
          return;
        }

        const filename = appState.result.videoFilename || deriveFilename(downloadUrl, 'generated-video.gif');
        await downloadAsset(downloadUrl, filename);

        console.log('✅ Video download completed');

        appState.setFeedbackType('download-video');
        appState.setShowFeedbackModal(true);
      } catch (error) {
        console.error('❌ Video download error:', error);
        alert('Video download failed. Please check the console for details.');
      }
      return;
    }

    // For other actions, just show feedback modal
    appState.setFeedbackType(type as any);
    appState.setShowFeedbackModal(true);
  }, [appState, deriveFilename, downloadAsset, resolveBackendUrl]);

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
