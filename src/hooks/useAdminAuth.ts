import { useCallback } from 'react';
import { useAppState } from './useAppState';

export const useAdminAuth = (appState: ReturnType<typeof useAppState>) => {
  const handleAdminLogin = useCallback(() => {
    if (appState.adminCredentials.username === 'admin' && appState.adminCredentials.password === 'admin') {
      appState.setIsAdminAuthenticated(true);
      appState.setCurrentView('admin');
      appState.setShowAdminLogin(false);
      appState.setAdminCredentials({ username: '', password: '' });
    } else {
      alert('Invalid credentials! Username: admin, Password: admin');
    }
  }, [appState]);

  const handleAdminLogout = useCallback(() => {
    appState.setIsAdminAuthenticated(false);
    appState.setCurrentView('welcome');
  }, [appState]);

  return { handleAdminLogin, handleAdminLogout };
};
