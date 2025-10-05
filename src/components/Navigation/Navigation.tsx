import React from 'react';
import { Menu, X, Lock } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import './Navigation.css';

interface NavigationProps {
  menuOpen: boolean;
  setMenuOpen: (open: boolean) => void;
  onAdminClick: () => void;
  onGetStartedClick: () => void;
}

export const Navigation: React.FC<NavigationProps> = ({
  menuOpen,
  setMenuOpen,
  onAdminClick
}) => {
  return (
    <nav className="nav">
      <div className="nav-container">
        <div className="nav-logo">
          <span className="logo-text">Agentic Ads</span>
          <span className="logo-emoji">✨</span>
        </div>
        <button className="menu-toggle" onClick={() => setMenuOpen(!menuOpen)}>
          {menuOpen ? <X size={24} /> : <Menu size={24} />}
        </button>
        <div className={`nav-links ${menuOpen ? 'active' : ''}`}>
          <a href="#features" onClick={(e) => { e.preventDefault(); document.getElementById('features')?.scrollIntoView({ behavior: 'smooth' }); }}>Features</a>
          <a href="#how" onClick={(e) => { e.preventDefault(); document.getElementById('how')?.scrollIntoView({ behavior: 'smooth' }); }}>How It Works</a>
          <a href="#developer" onClick={(e) => { e.preventDefault(); document.getElementById('developer')?.scrollIntoView({ behavior: 'smooth' }); }}>Developers</a>
          <Button variant="admin" onClick={onAdminClick}>
            <Lock size={16} />
            Admin
          </Button>
        </div>
      </div>
    </nav>
  );
};
