import { useState, useEffect, useCallback } from 'react';
import { ViewType, FormData, GenerationResult, Feedback, AdminCredentials, FeedbackType } from '@/types';

export const useAppState = () => {
  const [currentView, setCurrentView] = useState<ViewType>(() => {
    const saved = localStorage.getItem('currentView');
    return (saved as ViewType) || 'welcome';
  });
  const [menuOpen, setMenuOpen] = useState(false);
  const [showAdminLogin, setShowAdminLogin] = useState(false);
  const [showFeedbackModal, setShowFeedbackModal] = useState(false);
  const [feedbackType, setFeedbackType] = useState<FeedbackType>(null);
  const [adminToken, setAdminToken] = useState<string | null>(() => localStorage.getItem('adminToken'));
  const [isAdminAuthenticated, setIsAdminAuthenticated] = useState(() => {
    if (adminToken) {
      return true;
    }
    return localStorage.getItem('isAdminAuthenticated') === 'true';
  });
  const [generating, setGenerating] = useState(false);
  const [result, setResult] = useState<GenerationResult | null>(null);

  // Persist state to localStorage whenever it changes
  useEffect(() => {
    localStorage.setItem('currentView', currentView);
  }, [currentView]);

  useEffect(() => {
    if (adminToken) {
      localStorage.setItem('adminToken', adminToken);
    } else {
      localStorage.removeItem('adminToken');
    }
  }, [adminToken]);

  useEffect(() => {
    localStorage.setItem('isAdminAuthenticated', isAdminAuthenticated ? 'true' : 'false');
  }, [isAdminAuthenticated]);

  const clearAppState = useCallback(() => {
    localStorage.removeItem('currentView');
    localStorage.removeItem('isAdminAuthenticated');
    localStorage.removeItem('adminToken');
  }, []);

  const resetToWelcome = useCallback(() => {
    setCurrentView('welcome');
    setIsAdminAuthenticated(false);
    setAdminToken(null);
    clearAppState();
  }, [clearAppState, setAdminToken]);

  const [formData, setFormData] = useState<FormData>({
    adText: '',
    tone: 'professional',
    platform: 'Instagram',
    outputs: [], // Start with no outputs selected, let users choose
    logoPosition: 'bottom-right',
    logo: undefined
  });

  const [feedback, setFeedback] = useState<Feedback>({
    email: '',
    message: '',
    rating: 5
  });

  const [adminCredentials, setAdminCredentials] = useState<AdminCredentials>({
    username: '',
    password: ''
  });

  return {
    currentView,
    setCurrentView,
    menuOpen,
    setMenuOpen,
    showAdminLogin,
    setShowAdminLogin,
    showFeedbackModal,
    setShowFeedbackModal,
    feedbackType,
    setFeedbackType,
    isAdminAuthenticated,
    setIsAdminAuthenticated,
    generating,
    setGenerating,
    result,
    setResult,
    adminToken,
    setAdminToken,
    formData,
    setFormData,
    feedback,
    setFeedback,
    adminCredentials,
    setAdminCredentials,
    clearAppState,
    resetToWelcome
  };
};
