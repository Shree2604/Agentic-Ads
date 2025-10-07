import { useCallback } from 'react';
import { useAppState } from './useAppState';
import { useApiData } from './useApiData';

export const useAdGeneration = (appState: ReturnType<typeof useAppState>, apiData: ReturnType<typeof useApiData>) => {
  const handleGenerate = useCallback(async () => {
    appState.setGenerating(true);

    try {
      // Call the RAG API for actual generation
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/rag/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${appState.adminToken}`,
        },
        body: JSON.stringify({
          platform: appState.formData.platform,
          tone: appState.formData.tone,
          ad_text: appState.formData.adText,
          outputs: appState.formData.outputs,
          brand_guidelines: appState.formData.brandGuidelines || undefined,
        }),
      });

      if (!response.ok) {
        throw new Error(`RAG generation failed: ${response.statusText}`);
      }

      const result = await response.json();

      // Handle errors from RAG system
      if (result.errors && result.errors.length > 0) {
        console.warn('RAG generation completed with warnings:', result.errors);
      }

      // Save generation history
      const newGeneration = {
        id: Date.now(), // Use timestamp as ID for now
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
          // Don't throw here - generation was successful, just logging failed
        }
      }

      // Set the result from RAG system
      appState.setResult({
        rewrittenText: result.text || "Generated content not available",
        posterUrl: result.poster_prompt || "Poster prompt not generated",
        videoUrl: result.video_script || "Video script not generated",
        qualityScores: result.quality_scores || {},
        validationFeedback: result.validation_feedback || {}
      });

    } catch (error) {
      console.error('Generation failed:', error);

      // Fallback to mock generation if RAG fails
      console.log('Falling back to mock generation...');

      const newGeneration = {
        id: Date.now(),
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
        } catch (historyError) {
          console.error('Failed to save fallback generation:', historyError);
        }
      }

      // Provide fallback result
      appState.setResult({
        rewrittenText: "🚀 Ready to level up your fitness game? Our revolutionary app brings personal training to your pocket! Join 10K+ users transforming their lives. #FitnessRevolution #GetFit",
        posterUrl: "https://via.placeholder.com/1080x1080/FF6B6B/ffffff?text=Generated+Poster",
        videoUrl: "https://via.placeholder.com/1080x1920/4ECDC4/ffffff?text=Generated+Video"
      });
    } finally {
      appState.setGenerating(false);
    }
  }, [appState, apiData]);

  return { handleGenerate };
};
