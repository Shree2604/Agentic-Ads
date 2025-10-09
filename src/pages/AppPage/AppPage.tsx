import React from 'react';
import { Type, Image, Video, Download, Copy, ArrowLeft } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { FormData, GenerationResult, OutputType, Platform, Tone } from '@/types';
import './AppPage.css';

interface PosterImageProps {
  url: string;
}

const PosterImage: React.FC<PosterImageProps> = ({ url }) => {
  const [imageError, setImageError] = React.useState(false);
  const [imageLoading, setImageLoading] = React.useState(true);

  const handleImageError = () => {
    setImageError(true);
    setImageLoading(false);
  };

  const handleImageLoad = () => {
    setImageLoading(false);
  };

  if (imageError) {
    return (
      <div className="poster-unavailable">
        <Image size={16} />
        <p>Preview Unavailable</p>
      </div>
    );
  }

  return (
    <>
      {imageLoading && (
        <div className="poster-loading">
          <div className="spinner"></div>
          <p>Loading preview...</p>
        </div>
      )}
      <img
        src={url}
        alt="Generated Poster"
        onError={handleImageError}
        onLoad={handleImageLoad}
        style={{ display: imageLoading ? 'none' : 'block' }}
      />
    </>
  );
};

interface AppPageProps {
  formData: FormData;
  setFormData: (data: FormData) => void;
  generating: boolean;
  result: GenerationResult | null;
  onGenerate: () => void;
  onBackToWelcome: () => void;
  onActionClick: (type: string) => void;
}

export const AppPage: React.FC<AppPageProps> = ({
  formData,
  setFormData,
  generating,
  result,
  onGenerate,
  onBackToWelcome,
  onActionClick
}) => {
  const platforms: Platform[] = ['Instagram', 'LinkedIn', 'Twitter', 'YouTube'];
  const tones: Tone[] = ['professional', 'casual', 'energetic', 'fun', 'witty'];
  const outputTypes: OutputType[] = [
    { id: 'text', label: 'Rewritten Text', icon: Type },
    { id: 'poster', label: 'Poster Image', icon: Image },
    { id: 'video', label: 'Video Reel', icon: Video }
  ];

  const toggleOutput = (output: string) => {
    setFormData({
      ...formData,
      outputs: formData.outputs.includes(output)
        ? formData.outputs.filter(o => o !== output)
        : [...formData.outputs, output]
    });
  };

  return (
    <div className="app-page">
      <header className="app-header">
        <div className="app-header-content">
          <div className="header-left">
            <button className="back-button" onClick={onBackToWelcome}>
              <ArrowLeft size={20} />
              Back to Welcome
            </button>
          </div>
          <div className="header-right">
            <div className="app-logo">
              <span className="logo-text">Agentic Ads</span>
              <span className="logo-emoji">✨</span>
            </div>
          </div>
        </div>
      </header>

      <div className="app-container">
        <div className="app-grid">
          <div className="form-section">
            <div className="form-card">
              <div className="form-header">
                <h2 className="form-title">Get Perfect Advertisement with Agentic Ads</h2>
              </div>
              
              <div className="form-group">
                <label>Your Ad Text</label>
                <textarea
                  placeholder="Enter your ad text here..."
                  value={formData.adText}
                  onChange={(e) => setFormData({...formData, adText: e.target.value})}
                  rows={10}
                />
              </div>

              <div className="form-group">
                <label>Your Logo</label>
                <input
                  type="file"
                  accept="image/*"
                  onChange={(e) => setFormData({...formData, logo: e.target.files?.[0]})}
                />
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label>Tone</label>
                  <select
                    value={formData.tone}
                    onChange={(e) => setFormData({...formData, tone: e.target.value})}
                  >
                    {tones.map(tone => (
                      <option key={tone} value={tone}>
                        {tone.charAt(0).toUpperCase() + tone.slice(1)}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="form-group">
                  <label>Platform</label>
                  <select
                    value={formData.platform}
                    onChange={(e) => setFormData({...formData, platform: e.target.value})}
                  >
                    {platforms.map(platform => (
                      <option key={platform} value={platform}>
                        {platform}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="form-group">
                <label>Output Types</label>
                <p className="form-hint">Select at least one output type to generate</p>
                <div className="output-types">
                  {outputTypes.map(({ id, label, icon: Icon }) => (
                    <div
                      key={id}
                      className={`output-type ${formData.outputs.includes(id) ? 'selected' : ''}`}
                      onClick={() => toggleOutput(id)}
                    >
                      <Icon size={20} />
                      <span>{label}</span>
                    </div>
                  ))}
                </div>
              </div>

              <Button
                variant="primary"
                onClick={onGenerate}
                disabled={generating || !formData.adText.trim() || formData.outputs.length === 0}
                className="generate-button"
              >
                {generating ? 'Generating...' : 'Generate Ad'}
              </Button>
            </div>
          </div>

          <div className="results-section">
            {generating && (
              <div className="generating-state">
                <div className="spinner"></div>
                <h3>Creating your perfect ad...</h3>
                <p>Our AI agents are working their magic</p>
              </div>
            )}
            {result && !generating && (
              <div className="results-card">
                
                
                {formData.outputs.includes('text') && result.rewrittenText && (
                  <div className="result-item">
                    <div className="result-header">
                      <div className="result-header-left">
                        <Type size={20} />
                        <span>Generated Text</span>
                      </div>
                      <Button
                        variant="outline"
                        onClick={() => onActionClick('copy')}
                        className="action-button"
                      >
                        <Copy size={16} />
                        Copy
                      </Button>
                    </div>
                    <div className="result-content">
                      <p>{result.rewrittenText}</p>
                      <p className="text-ready">✅ Text ready for use</p>
                    </div>
                  </div>
                )}

                {formData.outputs.includes('poster') && result.poster_url && (
                  <div className="result-item">
                    <div className="result-header">
                      <div className="result-header-left">
                        <Image size={20} />
                        <span>Generated Poster</span>
                      </div>
                      <Button
                        variant="outline"
                        onClick={() => onActionClick('download-poster')}
                        className="action-button"
                      >
                        <Download size={16} />
                        Download
                      </Button>
                    </div>
                    <div className="result-content">
                      <div className="poster-display">
                        <PosterImage url={result.poster_url} />
                      </div>
                    </div>
                  </div>
                )}

                {formData.outputs.includes('video') && (
                  <div className="result-item">
                    <div className="result-header">
                      <div className="result-header-left">
                        <Video size={20} />
                        <span>Generated Video</span>
                      </div>
                      <Button
                        variant="outline"
                        onClick={() => onActionClick('download-video')}
                        className="action-button"
                        disabled={!result.videoUrl}
                      >
                        <Download size={16} />
                        Download
                      </Button>
                    </div>
                    <div className="result-content">
                        <div className="video-placeholder">
                          <Video size={20} />
                          <p style={{color:'black'}}>Video preview unavailable</p>
                        </div>                      
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
