import { useState, useEffect } from 'react';
import { Zap, Wand2, Type, Image, Video, Sparkles, Check, Github, Linkedin, Mail, ChevronDown, Globe, Phone } from 'lucide-react';
import { Navigation } from '@/components/Navigation/Navigation';
import { Button } from '@/components/ui/Button';
import './WelcomePage.css';

interface WelcomePageProps {
  menuOpen: boolean;
  setMenuOpen: (open: boolean) => void;
  onAdminClick: () => void;
  onGetStartedClick: () => void;
}

export const WelcomePage: React.FC<WelcomePageProps> = ({
  menuOpen,
  setMenuOpen,
  onAdminClick,
  onGetStartedClick
}) => {
  const [showScrollIndicator, setShowScrollIndicator] = useState(true);

  useEffect(() => {
    const handleScroll = () => {
      const heroSection = document.querySelector('.hero');
      if (heroSection) {
        const rect = heroSection.getBoundingClientRect();
        const isHeroVisible = rect.bottom > 100; // Show if hero is still partially visible
        setShowScrollIndicator(isHeroVisible);
      }
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);
  return (
    <div className="welcome-page">
      <Navigation
        menuOpen={menuOpen}
        setMenuOpen={setMenuOpen}
        onAdminClick={onAdminClick}
        onGetStartedClick={onGetStartedClick}
      />

      <section className="hero">
        <div className="hero-background">
          <div className="gradient-orb orb-1"></div>
          <div className="gradient-orb orb-2"></div>
          <div className="gradient-orb orb-3"></div>
        </div>
        <div className="hero-content">
          <div className="badge">
            <Zap size={14} />
            <span>100% Free • Open Source • No Credit Card</span>
          </div>
          <h1 className="hero-title">
            Transform Your Ideas Into Platform Specific
            <br />
            <span className="gradient-text"> Multi-Model Advertisements</span>
          </h1>
          <div className="hero-cta">
            <Button variant="hero" onClick={onGetStartedClick}>
              <Wand2 size={20} />
              Start Creating Now
            </Button>
            <Button variant="secondary" onClick={() => document.getElementById('how')?.scrollIntoView({ behavior: 'smooth' })}>
              Watch Demo
            </Button>
          </div>
          {showScrollIndicator && (
            <div className="scroll-indicator" onClick={() => document.getElementById('features')?.scrollIntoView({ behavior: 'smooth' })}>
              <ChevronDown size={16} />
              <span>Scroll Down</span>
            </div>
          )}
        </div>
      </section>

      <section className="features" id="features">
        <div className="container">
          <h2 className="section-title">Everything You Need, Nothing You Don't</h2>
          <div className="features-grid">
            <div className="feature-card">
              <div className="feature-icon">
                <Type size={24} />
              </div>
              <h3>Smart Copywriting</h3>
              <br />
              <p>AI-powered text rewriting optimized for each platform's audiences style guidelines.</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">
                <Image size={24} />
              </div>
              <h3>Stunning Posters</h3>
              <br />
              <p>Generate eye-catching visuals with brand integration and platform-specific sizing.</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">
                <Video size={24} />
              </div>
              <h3>Engaging Videos</h3>
              <br />
              <p>Create professional video reels in seconds with your logo seamlessly integrated.</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">
                <Sparkles size={24} />
              </div>
              <h3>Brand Consistency</h3>
              <br />
              <p>Automatic logo overlay and brand color integration across all generated assets.</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">
                <Zap size={24} />
              </div>
              <h3>Lightning Fast</h3>
              <br />
              <p>Generate complete ad campaigns in under 180 seconds with our multi-agent system.</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">
                <Check size={24} />
              </div>
              <h3>Platform Perfect</h3>
              <br />
              <p>Agentic RAG ensures every ad meets platform-specific requirements.</p>
            </div>
          </div>
        </div>
      </section>

      <section className="how-it-works" id="how">
        <div className="container">
          <h2 className="section-title">How It Works</h2>
          <div className="videos-grid">
            <div className="video-block">
              <div className="video-header">
                <h3>For Tech Guys</h3>
                <p>Deep dive into the technical implementation details</p>
              </div>
              <div className="video-container">
                <iframe
                  width="100%"
                  height="400"
                  src="https://www.youtube.com/embed/i5MN8W6xBjw?autoplay=0&showinfo=0&controls=1"
                  title="AgenticAds Technical Demo"
                  frameBorder="0"
                  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                  allowFullScreen>
                </iframe>
              </div>
            </div>
            <div className="video-block">
              <div className="video-header">
                <h3>For Non-Tech Users</h3>
                <p>Simple walkthrough of how to use AgenticAds effectively</p>
              </div>
              <div className="video-container">
                <iframe
                  width="100%"
                  height="400"
                  src="https://www.youtube.com/embed/i0wvofuzU-Y?autoplay=0&showinfo=0&controls=1"
                  title="AgenticAds User Demo"
                  frameBorder="0"
                  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                  allowFullScreen>
                </iframe>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="developer-section" id="developer">
        <div className="container">
          <h2 className="section-title">Meet the Developer</h2>
          <p className="contact-info">If you are having any doubts or want to reach out to them you can contact him by using below links</p>
          <div className="developers-grid">
            <div className="developer-card">
              <div className="developer-image">
                <img 
                  src="/DSC_0454.JPG" 
                  alt="Agentic Ads Logo" 
                  className="developer-logo"
                />
              </div>
              <div className="developer-info">
                <div className="developer-heading">
                  <h3>Shreeraj Mummidivarapu</h3>
                  <p className="developer-title">BTech Final Year At IIIT Sricity <br></br> AI Dev At Vinfinet Technologies <br></br> Full Stack Agentic AI Developer <br></br> Edge, Federated & Transparent AI Researcher </p>
                </div>
                <div className="developer-links">
                  <a href="https://github.com/Shree2604" target="_blank" rel="noopener noreferrer" className="social-link">
                    <Github size={20} />
                    <span>GitHub</span>
                  </a>
                  <a href="https://www.linkedin.com/in/m-shreeraj/" target="_blank" rel="noopener noreferrer" className="social-link">
                    <Linkedin size={20} />
                    <span>LinkedIn</span>
                  </a>
                  <a href="https://shree-portfolio-ten.vercel.app/" target="_blank" rel="noopener noreferrer" className="social-link">
                    <Globe size={20} />
                    <span>Portfolio</span>
                  </a>
                  <a href="mailto:shree.xai.dev@gmail.com" target="_blank" rel="noopener noreferrer" className="social-link">
                    <Mail size={20} />
                    <span>shree.xai.dev@gmail.com</span>
                  </a>                  
                  <a href="tel:+918143272388" target="_blank" rel="noopener noreferrer" className="social-link">
                    <Phone size={20} />
                    <span>+91 8143272388</span>
                  </a>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

    </div>
  );
};
