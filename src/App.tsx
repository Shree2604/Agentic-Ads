import React from 'react';
import { WelcomePage } from '@/pages/WelcomePage/WelcomePage';
import { AppPage } from '@/pages/AppPage/AppPage';
import { AdminPage } from '@/pages/AdminPage/AdminPage';
import { AdminLogin } from '@/components/AdminLogin/AdminLogin';
import { FeedbackModal } from '@/components/FeedbackModal/FeedbackModal';
import { useAppState } from '@/hooks/useAppState';
import { useApiData } from '@/hooks/useApiData';
import { useAdGeneration } from '@/hooks/useAdGeneration';
import { useAdminAuth } from '@/hooks/useAdminAuth';
import { useFeedbackHandler } from '@/hooks/useFeedbackHandler';
import './App.css';

const App: React.FC = () => {
  const appState = useAppState();
  const apiData = useApiData(appState.adminToken);
  const adGeneration = useAdGeneration(appState, apiData);
  const adminAuth = useAdminAuth(appState);
  const feedbackHandler = useFeedbackHandler(appState, apiData);

  const renderCurrentView = () => {
    // If user is authenticated as admin, go to admin page
    if (appState.isAdminAuthenticated) {
      if (apiData.loading) {
        return <div className="admin-loading">Loading admin data...</div>;
      }

      if (apiData.error) {
        return <div className="admin-error">{apiData.error}</div>;
      }

      return (
        <AdminPage
          generationHistory={apiData.generationHistory}
          feedbackList={apiData.feedbackList}
          onLogout={adminAuth.handleAdminLogout}
        />
      );
    }

    switch (appState.currentView) {
      case 'welcome':
        return (
          <WelcomePage
            menuOpen={appState.menuOpen}
            setMenuOpen={appState.setMenuOpen}
            onAdminClick={() => appState.setShowAdminLogin(true)}
            onGetStartedClick={() => appState.setCurrentView('app')}
          />
        );
      
      case 'app':
        return (
          <AppPage
            formData={appState.formData}
            setFormData={appState.setFormData}
            generating={appState.generating}
            result={appState.result}
            onGenerate={adGeneration.handleGenerate}
            onBackToWelcome={() => appState.setCurrentView('welcome')}
            onActionClick={feedbackHandler.handleActionClick}
          />
        );
      
      case 'admin':
        return (
          <AdminPage
            generationHistory={apiData.generationHistory}
            feedbackList={apiData.feedbackList}
            onLogout={adminAuth.handleAdminLogout}
          />
        );
      
      default:
        return null;
    }
  };

  return (
    <div className="app">
      {renderCurrentView()}
      
      <AdminLogin
        isOpen={appState.showAdminLogin}
        onClose={() => appState.setShowAdminLogin(false)}
        credentials={appState.adminCredentials}
        setCredentials={appState.setAdminCredentials}
        onLogin={adminAuth.handleAdminLogin}
      />

      <FeedbackModal
        isOpen={appState.showFeedbackModal}
        onClose={() => appState.setShowFeedbackModal(false)}
        feedback={appState.feedback}
        setFeedback={appState.setFeedback}
        onSubmit={feedbackHandler.submitFeedback}
      />
    </div>
  );
};

export default App;
