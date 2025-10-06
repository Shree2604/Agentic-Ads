import { useCallback } from 'react';
import { API_BASE_URL } from '@/config/api';
import { useAppState } from './useAppState';

export const useAdminAuth = (appState: ReturnType<typeof useAppState>) => {
  const handleAdminLogin = useCallback(async () => {
    const { username, password } = appState.adminCredentials;

    try {
      const response = await fetch(`${API_BASE_URL}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username, password })
      });

      if (!response.ok) {
        throw new Error('Invalid credentials');
      }

      const data = await response.json();

      appState.setAdminToken(data.access_token);
      appState.setIsAdminAuthenticated(true);
      appState.setCurrentView('admin');
      appState.setShowAdminLogin(false);
      appState.setAdminCredentials({ username: '', password: '' });
    } catch (error) {
      console.error('Admin login failed:', error);
      alert('Invalid credentials. Please try again.');
    }
  }, [appState]);

  const handleAdminLogout = useCallback(() => {
    appState.setAdminToken(null);
    appState.setIsAdminAuthenticated(false);
    appState.resetToWelcome();
  }, [appState]);

  return { handleAdminLogin, handleAdminLogout };
};
