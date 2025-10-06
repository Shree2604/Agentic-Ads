import React, { useState } from 'react';
import { Star, ArrowLeft } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { FeedbackItem } from '@/types';
import './InsightsPage.css';

interface InsightsPageProps {
  feedbackList: FeedbackItem[];
  onBack: () => void;
}

export const InsightsPage: React.FC<InsightsPageProps> = ({
  feedbackList,
  onBack
}) => {
  const [ratingFilter, setRatingFilter] = useState('');
  const [platformFilter, setPlatformFilter] = useState('');

  const filteredFeedback = feedbackList.filter(item => {
    const matchesRating = !ratingFilter || item.rating === parseInt(ratingFilter);
    const matchesPlatform = !platformFilter || item.platform === platformFilter;
    return matchesRating && matchesPlatform;
  });
  const avgRating = filteredFeedback.length > 0 
    ? (filteredFeedback.reduce((sum, f) => sum + f.rating, 0) / filteredFeedback.length).toFixed(1)
    : '0.0';

  const totalUsers = new Set(filteredFeedback.map(f => f.email)).size;

  return (
    <div className="insights-page">
      <header className="insights-header">
        <div className="insights-header-content">
          <div className="header-left">
            <Button variant="outline" onClick={onBack} className="back-button">
              <ArrowLeft size={20} />
              Back to Dashboard
            </Button>
          </div>
          <div className="header-right">
            <div className="page-title">
              <Star size={20} />
              <h2>Customer Insights</h2>
            </div>
          </div>
        </div>
      </header>

      <div className="insights-container">
        <div className="insights-top-section">
          <div className="stat-box">
            <span className="stat-value">{avgRating}</span>
            <span className="stat-label">Avg Rating</span>
          </div>
          <div className="stat-box">
            <span className="stat-value">{totalUsers}</span>
            <span className="stat-label">Total Users</span>
          </div>
          <div className="stat-box">
            <span className="stat-value">{filteredFeedback.length}</span>
            <span className="stat-label">Total Reviews</span>
          </div>

          <div className="filter-group">
            <label>Filter by Rating</label>
            <select
              className="filter-select"
              value={ratingFilter}
              onChange={(e) => setRatingFilter(e.target.value)}
            >
              <option value="">All Ratings</option>
              <option value="5">5 Stars</option>
              <option value="4">4 Stars</option>
              <option value="3">3 Stars</option>
              <option value="2">2 Stars</option>
              <option value="1">1 Star</option>
            </select>
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
        </div>
        <div className="feedback-cards-grid">
          {filteredFeedback.length === 0 ? (
            <div style={{ gridColumn: '1 / -1', textAlign: 'center', padding: '2rem', color: 'var(--text-secondary)' }}>
              No feedback matches the selected filters.
            </div>
          ) : (
            filteredFeedback.slice(0, 6).map((feedback) => (
            <div key={feedback.id} className="insights-card">
              <div className="insights-card-header">
                <div className="insights-card-title">
                  <div className="user-info">
                    <div>
                      <h3>{feedback.email}</h3>
                      <span className="feedback-date">{feedback.date}</span>
                    </div>
                  </div>
                  <div className="rating-platform">
                    <div className="stars">
                      {'★'.repeat(feedback.rating)}{'☆'.repeat(5-feedback.rating)}
                    </div>
                    <span className="platform-tag">{feedback.platform}</span>
                  </div>
                </div>
              </div>
              
              <div className="insights-card-content">
                <div className="feedback-message">
                  <p>"{feedback.message}"</p>
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
