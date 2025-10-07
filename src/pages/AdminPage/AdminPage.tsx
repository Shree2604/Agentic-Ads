import React, { useState } from 'react';
import { Lock, FileText, Users, Calendar, Star, Activity, PieChart, Clock, Database, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { GenerationHistory, FeedbackItem } from '@/types';
import { ActivityPage } from '../ActivityPage/ActivityPage';
import { InsightsPage } from '../InsightsPage/InsightsPage';
import './AdminPage.css';

interface AdminPageProps {
  generationHistory: GenerationHistory[];
  feedbackList: FeedbackItem[];
  onLogout: () => void;
}

export const AdminPage: React.FC<AdminPageProps> = ({
  generationHistory,
  feedbackList,
  onLogout
}) => {
  const avgRating = feedbackList.length > 0
    ? (feedbackList.reduce((sum, f) => sum + f.rating, 0) / feedbackList.length).toFixed(1)
    : '0.0';
  const totalUsers = new Set(feedbackList.map(f => f.email)).size;
  const totalGenerations = generationHistory.length;

  // Chart data calculations
  const platformStats = generationHistory.reduce((acc, item) => {
    acc[item.platform] = (acc[item.platform] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  const toneStats = generationHistory.reduce((acc, item) => {
    acc[item.tone] = (acc[item.tone] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  const [activeSection, setActiveSection] = useState('dashboard');
  const [isSeedingKnowledge, setIsSeedingKnowledge] = useState(false);
  const [seedMessage, setSeedMessage] = useState('');

  const handleSectionChange = (section: string) => {
    setActiveSection(section);
  };

  const handleBackToDashboard = () => {
    setActiveSection('dashboard');
  };

  const handleSeedKnowledgeBase = async () => {
    setIsSeedingKnowledge(true);
    setSeedMessage('');

    try {
      // Get admin token from localStorage
      const token = localStorage.getItem('adminToken');
      if (!token) {
        setSeedMessage('❌ Admin authentication required');
        return;
      }

      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/rag/seed-knowledge`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setSeedMessage(`✅ ${data.message}`);
      } else {
        const error = await response.text();
        setSeedMessage(`❌ Failed to seed knowledge base: ${error}`);
      }
    } catch (error) {
      setSeedMessage(`❌ Network error: ${error}`);
    } finally {
      setIsSeedingKnowledge(false);
    }
  };

  // Render different pages based on active section
  if (activeSection === 'activity') {
    return <ActivityPage generationHistory={generationHistory} onBack={handleBackToDashboard} />;
  }

  if (activeSection === 'insights') {
    return <InsightsPage feedbackList={feedbackList} onBack={handleBackToDashboard} />;
  }

  return (
    <div className="admin-dashboard">
      <header className="admin-header">
        <div className="admin-header-content">
          <div className="app-logo">
            <span className="logo-text">Agentic Ads</span>
            <span className="logo-emoji">✨</span>
          </div>
          <Button variant="outline-small" onClick={onLogout} className="logout-button">
            <Lock size={16} />
            Logout
          </Button>
        </div>
      </header>

      <div className="admin-container">
        <div className="dashboard-header">
          <h1 className="admin-title">Admin Analytics Dashboard</h1>
          <div className="dashboard-nav">
            <button className={`nav-tab ${activeSection === 'activity' ? 'active' : ''}`} onClick={() => handleSectionChange('activity')}>
              <Calendar size={20} />
              Recent Activity
            </button>
            <button className={`nav-tab ${activeSection === 'insights' ? 'active' : ''}`} onClick={() => handleSectionChange('insights')}>
              <Star size={20} />
              Customer Insights
            </button>
          </div>
        </div>

        {/* RAG System Controls */}
        <div className="rag-controls-section">
          <div className="rag-controls-header">
          </div>
          <div className="rag-controls">
            <Button
              onClick={handleSeedKnowledgeBase}
              disabled={isSeedingKnowledge}
              className="seed-knowledge-btn"
            >
              {isSeedingKnowledge ? (
                <>
                  <Loader2 size={16} className="animate-spin" />
                  Seeding Knowledge Base...
                </>
              ) : (
                <>
                  <Database size={16} />
                  Seed RAG Knowledge Base
                </>
              )}
            </Button>
            {seedMessage && (
              <div className={`seed-message ${seedMessage.includes('✅') ? 'success' : 'error'}`}>
                {seedMessage}
              </div>
            )}
          </div>
        </div>

        <div className="stats-grid">
          <div className="stat-card primary-metric">
            <div className="stat-card-icon stat-red">
              <FileText size={28} />
            </div>
            <div className="stat-card-content">
              <div className="stat-card-value">{totalGenerations}</div>
              <div className="stat-card-label">Total Generations</div>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-card-icon stat-blue">
              <Users size={28} />
            </div>
            <div className="stat-card-content">
              <div className="stat-card-value">{totalUsers}</div>
              <div className="stat-card-label">Active Users</div>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-card-icon stat-green">
              <Star size={28} />
            </div>
            <div className="stat-card-content">
              <div className="stat-card-value">{avgRating}</div>
              <div className="stat-card-label">Avg Rating</div>
            </div>
          </div>


        </div>

        <div className="charts-section">
          <div className="chart-card platform-chart">
            <div className="chart-header">
              <h3>
                <Activity size={20} />
                Platform Performance
              </h3>
              <div className="chart-actions">
                <span className="chart-period">Last 30 days</span>
              </div>
            </div>
            <div className="chart-content">
              <div className="chart-bars">
                {Object.entries(platformStats).map(([platform, count]) => {
                  const percentage = (count / totalGenerations) * 100;
                  return (
                    <div key={platform} className="chart-bar-item">
                      <div className="chart-bar">
                        <div
                          className="chart-fill"
                          style={{ width: `${percentage}%` }}
                        ></div>
                      </div>
                      <div className="chart-label">
                        <span className="platform-name">{platform}</span>
                        <div className="platform-stats">
                          <span className="platform-count">{count}</span>
                          <span className="platform-percentage">{percentage.toFixed(1)}%</span>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>

          <div className="chart-card pie-chart-card">
            <div className="chart-header">
              <h3>
                <PieChart size={20} />
                Content Tone Analysis
              </h3>
              <div className="chart-actions">
                <span className="chart-total">{totalGenerations} total</span>
              </div>
            </div>
            <div className="chart-content">
              <div className="pie-chart-container">
                <div className="pie-chart">
                  <svg viewBox="0 0 200 200" className="pie-svg">
                    {(() => {
                      const colors = ['#6366f1', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'];
                      let currentAngle = 0;

                      return Object.entries(toneStats).map(([tone, count], index) => {
                        const percentage = (count / totalGenerations) * 100;
                        const angle = (percentage / 100) * 360;
                        const startAngle = currentAngle;
                        const endAngle = currentAngle + angle;
                        currentAngle = endAngle;

                        const largeArcFlag = angle > 180 ? 1 : 0;
                        const startAngleRad = (startAngle * Math.PI) / 180;
                        const endAngleRad = (endAngle * Math.PI) / 180;

                        const x1 = 100 + 90 * Math.cos(startAngleRad);
                        const y1 = 100 + 90 * Math.sin(startAngleRad);
                        const x2 = 100 + 90 * Math.cos(endAngleRad);
                        const y2 = 100 + 90 * Math.sin(endAngleRad);

                        const pathData = [
                          `M 100 100`,
                          `L ${x1} ${y1}`,
                          `A 90 90 0 ${largeArcFlag} 1 ${x2} ${y2}`,
                          'Z'
                        ].join(' ');

                        return (
                          <path
                            key={tone}
                            d={pathData}
                            fill={colors[index % colors.length]}
                            stroke="white"
                            strokeWidth="2"
                            className="pie-segment"
                          />
                        );
                      });
                    })()}
                    <circle cx="100" cy="100" r="45" fill="white" />
                    <text x="100" y="95" textAnchor="middle" className="pie-center-text">
                      <tspan className="pie-total">{totalGenerations}</tspan>
                      <tspan x="100" y="110" className="pie-label">Total</tspan>
                    </text>
                  </svg>
                </div>
                <div className="pie-legend">
                  {Object.entries(toneStats).map(([tone, count], index) => {
                    const colors = ['#6366f1', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'];
                    const percentage = (count / totalGenerations) * 100;
                    return (
                      <div key={tone} className="legend-item">
                        <div className="legend-color" style={{ backgroundColor: colors[index % colors.length] }}></div>
                        <span className="legend-label">{tone}</span>
                        <span className="legend-value">{count} ({percentage.toFixed(1)}%)</span>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          </div>
        </div>
        <div className="data-section">
          {activeSection === 'activity' && (
            <div className="admin-grid">
              <div className="admin-section activity-section">
                <div className="section-header">
                  <h2>
                    <Calendar size={20} />
                    Recent Activity
                  </h2>
                  <div className="section-actions">
                    <span className="activity-count">{generationHistory.length} total generations</span>
                    <div className="activity-filters">
                      <select className="activity-filter">
                        <option value="">All Platforms</option>
                        <option value="Instagram">Instagram</option>
                        <option value="LinkedIn">LinkedIn</option>
                        <option value="Twitter">Twitter</option>
                        <option value="YouTube">YouTube</option>
                      </select>
                      <select className="activity-filter">
                        <option value="">All Status</option>
                        <option value="Completed">Completed</option>
                        <option value="Processing">Processing</option>
                        <option value="Failed">Failed</option>
                      </select>
                    </div>
                  </div>
                </div>
                <div className="activity-cards">
                  {generationHistory.slice(0, 6).map((item) => (
                    <div key={item.id} className="activity-card">
                      <div className="activity-card-header">
                        <div className="activity-card-title">
                          <h3>Generation #{item.id}</h3>
                          <span className={`status-badge ${item.status.toLowerCase()}`}>
                            {item.status}
                          </span>
                        </div>
                        <div className="activity-card-time">
                          <Clock size={14} />
                          <span>{item.date} {item.time}</span>
                        </div>
                      </div>

                      <div className="activity-card-content">
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
                        <div className="activity-card-row">
                          <span className="activity-card-label">Performance:</span>
                          <div className="performance-indicator">
                            <div className="performance-bar">
                              <div className="performance-fill" style={{ width: `${75 + (item.id % 20)}%` }}></div>
                            </div>
                            <span className="performance-score">{75 + (item.id % 20)}%</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {activeSection === 'insights' && (
            <div className="admin-grid">
              <div className="admin-section feedback-section">
                <div className="section-header">
                  <h2>
                    <Star size={20} />
                    Customer Insights
                  </h2>
                  <div className="section-actions">
                    <span className="feedback-summary">{avgRating}/5.0 avg rating</span>
                  </div>
                </div>
                <div className="feedback-list">
                  {feedbackList.slice(0, 6).map((feedback) => (
                    <div key={feedback.id} className="feedback-item">
                      <div className="feedback-header">
                        <div className="feedback-user">
                          <div className="user-avatar">
                            {feedback.email.charAt(0).toUpperCase()}
                          </div>
                          <div className="user-info">
                            <strong>{feedback.email}</strong>
                            <span className="feedback-action">{feedback.action}</span>
                          </div>
                        </div>
                        <div className="feedback-rating">
                          <div className="stars">
                            {'★'.repeat(feedback.rating)}{'☆'.repeat(5-feedback.rating)}
                          </div>
                          <span className="rating-number">{feedback.rating}/5</span>
                        </div>
                      </div>
                      <div className="feedback-message">
                        "{feedback.message}"
                      </div>
                      <div className="feedback-meta">
                        <span className="platform-tag">{feedback.platform}</span>
                        <span className="feedback-date">{feedback.date}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
