import React, { useState } from 'react';
import { Calendar, ArrowLeft } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { GenerationHistory } from '@/types';
import './ActivityPage.css';

interface ActivityPageProps {
  generationHistory: GenerationHistory[];
  onBack: () => void;
}

export const ActivityPage: React.FC<ActivityPageProps> = ({
  generationHistory,
  onBack
}) => {
  const [platformFilter, setPlatformFilter] = useState('');
  const [toneFilter, setToneFilter] = useState('');

  const filteredHistory = generationHistory.filter(item => {
    const matchesPlatform = !platformFilter || item.platform === platformFilter;
    const matchesTone = !toneFilter || item.tone.toLowerCase() === toneFilter.toLowerCase();
    return matchesPlatform && matchesTone;
  });

  return (
    <div className="activity-page">
      <header className="activity-header">
        <div className="activity-header-content">
          <div className="header-left">
            <Button variant="outline" onClick={onBack} className="back-button">
              <ArrowLeft size={20} />
              Back to Dashboard
            </Button>
          </div>
          <div className="header-right">
            <div className="page-title">
              <Calendar size={20} />
              <h2>Recent Activity</h2>
            </div>
          </div>
        </div>
      </header>

      <div className="activity-container">
        <div className="activity-top-section">
          <div className="stat-box">
            <span className="stat-value">{generationHistory.length}</span>
            <span className="stat-label">Total Generations</span>
          </div>
          <div className="stat-box">
            <span className="stat-value">{generationHistory.filter(item => item.status === 'Completed').length}</span>
            <span className="stat-label">Completed</span>
          </div>

          <div className="filter-group">
            <label>Filter by Platform</label>
            <select
              className="filter-select"
              value={platformFilter}
              onChange={(e) => setPlatformFilter(e.target.value)}
            >
              <option value="">All Platforms</option>
              <option value="Instagram">Instagram</option>
              <option value="LinkedIn">LinkedIn</option>
              <option value="Twitter">Twitter</option>
              <option value="YouTube">YouTube</option>
            </select>
          </div>
          <div className="filter-group">
            <label>Filter by Tone</label>
            <select
              className="filter-select"
              value={toneFilter}
              onChange={(e) => setToneFilter(e.target.value)}
            >
              <option value="">All Tones</option>
              <option value="professional">Professional</option>
              <option value="casual">Casual</option>
              <option value="energetic">Energetic</option>
              <option value="fun">Fun</option>
              <option value="witty">Witty</option>
            </select>
          </div>
        </div>

        <div className="activity-cards-grid">
          {filteredHistory.length === 0 ? (
            <div style={{ gridColumn: '1 / -1', textAlign: 'center', padding: '2rem', color: 'var(--text-secondary)' }}>
              No activities match the selected filters.
            </div>
          ) : (
            filteredHistory.slice(0, 6).map((item) => (
            <div key={item.id} className="activity-card">
              <div className="activity-card-header">
                <div className="activity-card-title">
                  <h3>Generation {item.id}</h3>
                  <span className={`status-badge ${item.status.toLowerCase()}`}>
                    {item.status}
                  </span>
                </div>
              </div>



              <div className="activity-card-content">
                <div className='activity-card-row'>
                  <span className="activity-card-label">Date & Time:</span>
                  <span className="outputs-count">{item.date} {item.time}</span>
                </div>
                <div className="activity-card-row">
                  <span className="activity-card-label">Platform:</span>
                  <span className="platform-badge">{item.platform}</span>
                </div>
                <div className="activity-card-row">
                  <span className="activity-card-label">Content Tone:</span>
                  <span className="tone-badge">{item.tone}</span>
                </div>
                <div className="activity-card-row">
                  <span className="activity-card-label">Outputs:</span>
                  <span className="outputs-count">{item.outputs}</span>
                </div>
              </div>
            </div>
          ))
          )}
        </div>
      </div>
    </div>
  );
};
