import { useCallback } from 'react';
import { useAppState } from './useAppState';
import { useDataState } from './useDataState';

export const useAdGeneration = (appState: ReturnType<typeof useAppState>, dataState: ReturnType<typeof useDataState>) => {
  const handleGenerate = useCallback(async () => {
    appState.setGenerating(true);
    
    // Simulate API call
    setTimeout(() => {
      const newGeneration = {
        id: dataState.generationHistory.length + 1,
        date: new Date().toISOString().split('T')[0],
        time: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
        platform: appState.formData.platform,
        tone: appState.formData.tone.charAt(0).toUpperCase() + appState.formData.tone.slice(1),
        adText: appState.formData.adText,
        outputs: appState.formData.outputs.map(o => o.charAt(0).toUpperCase() + o.slice(1)).join(', '),
        status: 'Completed'
      };
      
      dataState.setGenerationHistory([newGeneration, ...dataState.generationHistory]);
      
      appState.setResult({
        rewrittenText: "🚀 Ready to level up your fitness game? Our revolutionary app brings personal training to your pocket! Join 10K+ users transforming their lives. #FitnessRevolution #GetFit",
        posterUrl: "https://via.placeholder.com/1080x1080/FF6B6B/ffffff?text=Generated+Poster",
        videoUrl: "https://via.placeholder.com/1080x1920/4ECDC4/ffffff?text=Generated+Video"
      });
      
      appState.setGenerating(false);
    }, 3000);
  }, [appState, dataState]);

  return { handleGenerate };
};
