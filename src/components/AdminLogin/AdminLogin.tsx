import React from 'react';
import { Lock } from 'lucide-react';
import { Modal } from '@/components/ui/Modal';
import { FormGroup } from '@/components/ui/FormGroup';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';
import { AdminCredentials } from '@/types';
import './AdminLogin.css';

interface AdminLoginProps {
  isOpen: boolean;
  onClose: () => void;
  credentials: AdminCredentials;
  setCredentials: (credentials: AdminCredentials) => void;
  onLogin: () => void;
}

export const AdminLogin: React.FC<AdminLoginProps> = ({
  isOpen,
  onClose,
  credentials,
  setCredentials,
  onLogin
}) => {
  const handleUsernameChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setCredentials({ ...credentials, username: e.target.value });
  };

  const handlePasswordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setCredentials({ ...credentials, password: e.target.value });
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      onLogin();
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Admin Login"
      icon={<Lock size={24} />}
    >
      <FormGroup label="Username">
        <Input
          type="text"
          placeholder="Enter admin username"
          value={credentials.username}
          onChange={handleUsernameChange}
        />
      </FormGroup>
      <FormGroup label="Password">
        <Input
          type="password"
          placeholder="Enter admin password"
          value={credentials.password}
          onChange={handlePasswordChange}
          onKeyPress={handleKeyPress}
        />
      </FormGroup>
      <Button variant="modal-primary" onClick={onLogin}>
        Login
      </Button>
      <p className="admin-hint">Credentials: admin / admin</p>
    </Modal>
  );
};
