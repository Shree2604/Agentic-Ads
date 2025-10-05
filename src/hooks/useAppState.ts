import { useState } from 'react';
import { ViewType, FormData, GenerationResult, Feedback, AdminCredentials, FeedbackType } from '@/types';

export const useAppState = () => {
  const [currentView, setCurrentView] = useState<ViewType>('welcome');
  const [menuOpen, setMenuOpen] = useState(false);
  const [showAdminLogin, setShowAdminLogin] = useState(false);
  const [showFeedbackModal, setShowFeedbackModal] = useState(false);
  const [feedbackType, setFeedbackType] = useState<FeedbackType>(null);
  const [isAdminAuthenticated, setIsAdminAuthenticated] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [result, setResult] = useState<GenerationResult | null>(null);

  const [formData, setFormData] = useState<FormData>({
    adText: '',
    tone: 'professional',
    platform: 'Instagram',
    outputs: ['text', 'poster', 'video'],
    logoPosition: 'bottom-right'
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
    formData,
    setFormData,
    feedback,
    setFeedback,
    adminCredentials,
    setAdminCredentials
  };
};
