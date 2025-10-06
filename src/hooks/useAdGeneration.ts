import { useCallback } from 'react';
import { useAppState } from './useAppState';
import { useApiData } from './useApiData';

export const useAdGeneration = (appState: ReturnType<typeof useAppState>, apiData: ReturnType<typeof useApiData>) => {
  const handleGenerate = useCallback(async () => {
    appState.setGenerating(true);
    
    // Simulate API call
    setTimeout(async () => {
      const newGeneration = {
        id: 0, // Will be set by backend
        date: new Date().toISOString().split('T')[0],
        time: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
        platform: appState.formData.platform,
        tone: appState.formData.tone.charAt(0).toUpperCase() + appState.formData.tone.slice(1),
        adText: appState.formData.adText,
        outputs: appState.formData.outputs.map(o => o.charAt(0).toUpperCase() + o.slice(1)).join(', '),
        status: 'Completed'
      };
      
      if (appState.adminToken) {
        try {
          await apiData.addGenerationHistory(newGeneration);
        } catch (error) {
          console.error('Failed to save generation:', error);
          alert('Unable to persist generation history. Please try again.');
        }
      }
      
      appState.setResult({
        rewrittenText: "🚀 Ready to level up your fitness game? Our revolutionary app brings personal training to your pocket! Join 10K+ users transforming their lives. #FitnessRevolution #GetFit",
        posterUrl: "https://via.placeholder.com/1080x1080/FF6B6B/ffffff?text=Generated+Poster",
        videoUrl: "https://via.placeholder.com/1080x1920/4ECDC4/ffffff?text=Generated+Video"
      });
      
      appState.setGenerating(false);
    }, 3000);
  }, [appState, apiData]);

  return { handleGenerate };
};
