import { useCallback } from 'react';
import { useAppState } from './useAppState';
import { useApiData } from './useApiData';

export const useAdGeneration = (appState: ReturnType<typeof useAppState>, apiData: ReturnType<typeof useApiData>) => {

  const handleGenerate = useCallback(async () => {
    appState.setGenerating(true);

    try {
      // Check if logo file is provided to decide which endpoint to use
      const hasLogo = !!appState.formData.logo;
      const endpoint = hasLogo ? 'generate-with-logo' : 'generate';

      console.log('Making RAG API request to:', `http://localhost:8000/api/rag/${endpoint}`);
      console.log('Request payload:', {
        platform: appState.formData.platform,
        tone: appState.formData.tone,
        ad_text: appState.formData.adText,
        outputs: appState.formData.outputs,
        brand_guidelines: appState.formData.brandGuidelines || undefined,
        logo_file: hasLogo ? 'file_provided' : undefined,
        logo_position: 'top-right',
      });

      let response: Response;

      if (hasLogo) {
        // Use FormData for file upload
        const formData = new FormData();
        formData.append('platform', appState.formData.platform);
        formData.append('tone', appState.formData.tone);
        formData.append('ad_text', appState.formData.adText);
        formData.append('outputs', appState.formData.outputs.join(','));
        if (appState.formData.brandGuidelines) {
          formData.append('brand_guidelines', appState.formData.brandGuidelines);
        }
        formData.append('logo_position', 'top-right');
        formData.append('logo_file', appState.formData.logo!);

        response = await fetch(`http://localhost:8000/api/rag/${endpoint}`, {
          method: 'POST',
          body: formData, // No Content-Type header needed for FormData
        });
      } else {
        // Use JSON for requests without logo
        response = await fetch(`http://localhost:8000/api/rag/${endpoint}`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            platform: appState.formData.platform,
            tone: appState.formData.tone,
            ad_text: appState.formData.adText,
            outputs: appState.formData.outputs,
            brand_guidelines: appState.formData.brandGuidelines || undefined,
            logo_position: 'top-right',
          }),
        });
      }

      console.log('Response status:', response.status);
      console.log('Response headers:', Object.fromEntries(response.headers.entries()));

      if (!response.ok) {
        const errorText = await response.text();
        console.error('API Error response:', errorText);
        throw new Error(`RAG generation failed: ${response.statusText}`);
      }

      const result = await response.json();
      console.log('Raw API response:', result);

      // Handle errors from RAG system
      if (result.errors && result.errors.length > 0) {
        console.warn('RAG generation completed with warnings:', result.errors);
      }

      // Save generation history for all users (not just admins)
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

      try {
        await apiData.addGenerationHistory(newGeneration);
        console.log('✅ Generation history saved to database');
      } catch (error) {
        console.error('❌ Failed to save generation history:', error);
        // Don't throw here - generation was successful, just logging failed
      }

      // Set the result from RAG system
      console.log('RAG Generation result:', result);
      console.log('RAG Generation result.text:', result.text);
      console.log('RAG Generation result.poster_prompt:', result.poster_prompt);
      console.log('RAG Generation result.poster_url:', result.poster_url);
      console.log('RAG Generation result.video_script:', result.video_script);

      // Check if we got empty results (indicating API issues)
      const hasEmptyResults = !result.text && !result.poster_prompt && !result.video_script;
      console.log('hasEmptyResults:', hasEmptyResults);
      if (hasEmptyResults) {
        console.warn('No content received from RAG API - all fields are empty');
      }

      appState.setResult({
        rewrittenText: result.text || (hasEmptyResults ? 
          "🤖 AI generation temporarily unavailable. Using smart templates instead.\n\n🚀 Ready to level up your business? Our premium solutions deliver exceptional results!" :
          "Generated content not available"),
        posterUrl: result.poster_prompt || (hasEmptyResults ? 
          "Create a stunning visual advertisement featuring premium quality and professional design elements for maximum engagement." :
          "Poster prompt not generated"),
        poster_url: result.poster_url || undefined, // New base64 poster field
        videoUrl: result.video_script || (hasEmptyResults ? 
          "SCENE 1: Dynamic opening with energetic music\nNARRATION: Transform your business today!\n\nSCENE 2: Show product benefits\nNARRATION: See the difference quality makes\n\nSCENE 3: Strong call-to-action\nNARRATION: Contact us now for premium solutions!" :
          "Video script not generated"),
        qualityScores: result.quality_scores || {},
        validationFeedback: result.validation_feedback || {}
      });
    } catch (error) {

      // Fallback to mock generation if RAG fails
      console.log('Falling back to mock generation...');

      const fallbackGeneration = {
        id: Date.now(),
        date: new Date().toISOString().split('T')[0],
        time: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
        platform: appState.formData.platform,
        tone: appState.formData.tone.charAt(0).toUpperCase() + appState.formData.tone.slice(1),
        adText: appState.formData.adText,
        outputs: appState.formData.outputs.map(o => o.charAt(0).toUpperCase() + o.slice(1)).join(', '),
        status: 'Fallback'
      };

      try {
        await apiData.addGenerationHistory(fallbackGeneration);
        console.log('✅ Fallback generation history saved to database');
      } catch (historyError) {
        console.error('❌ Failed to save fallback generation history:', historyError);
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
