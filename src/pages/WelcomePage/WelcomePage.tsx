import { useState, useEffect } from 'react';
import { Zap, Wand2, Type, Image, Video, Sparkles, Check, Github, Linkedin, Mail, Play, ChevronDown, Globe } from 'lucide-react';
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
            Transform Your Ideas Into
            <span className="gradient-text"> Platform-Perfect Multi-Model Ads</span>
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
              <p>AI-powered text rewriting optimized for each platform's audience and style guidelines.</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">
                <Image size={24} />
              </div>
              <h3>Stunning Posters</h3>
              <p>Generate eye-catching visuals with automatic brand integration and platform-specific sizing.</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">
                <Video size={24} />
              </div>
              <h3>Engaging Videos</h3>
              <p>Create professional video reels in seconds with your logo seamlessly integrated.</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">
                <Sparkles size={24} />
              </div>
              <h3>Brand Consistency</h3>
              <p>Automatic logo overlay and brand color integration across all generated assets.</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">
                <Zap size={24} />
              </div>
              <h3>Lightning Fast</h3>
              <p>Generate complete ad campaigns in under 60 seconds with our multi-agent system.</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">
                <Check size={24} />
              </div>
              <h3>Platform Perfect</h3>
              <p>Graph RAG ensures every ad meets platform-specific requirements automatically.</p>
            </div>
          </div>
        </div>
      </section>

      <section className="how-it-works" id="how">
        <div className="container">
          <h2 className="section-title">How It Works</h2>
          <div className="video-container">
            <div className="video-placeholder">
              <Play size={64} />
              <h3>Demo Video Coming Soon</h3>
              <p>Watch how AgenticAds transforms your ideas into perfect ads</p>
            </div>
            {/* YouTube embed will be added here later */}
            {/* <iframe 
              width="100%" 
              height="400" 
              src="https://www.youtube.com/embed/YOUR_VIDEO_ID" 
              title="AgenticAds Demo" 
              frameBorder="0" 
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
              allowFullScreen>
            </iframe> */}
          </div>
        </div>
      </section>

      <section className="developer-section" id="developer">
        <div className="container">
          <h2 className="section-title">Meet the Developers</h2>
          <p className="contact-info">If you are having any doubts or want to reach out to them you can contact them by using below links</p>
          <div className="developers-grid">
            <div className="developer-card">
              <div className="developer-image">
                <div className="avatar-placeholder">
                  <span>SM</span>
                </div>
              </div>
              <div className="developer-info">
                <h3>Shreeraj Mummidivarapu</h3>
                <p className="developer-title">Full Stack AI Developer</p>
                <div className="developer-links">
                  <a href="https://github.com/shreeraj" target="_blank" rel="noopener noreferrer" className="social-link" title="GitHub">
                    <Github size={20} />
                  </a>
                  <a href="https://linkedin.com/in/shreeraj" target="_blank" rel="noopener noreferrer" className="social-link" title="LinkedIn">
                    <Linkedin size={20} />
                  </a>
                  <a href="mailto:shree.xai.dev@gmail.com" className="social-link" title="Email">
                    <Mail size={20} />
                  </a>
                  <a href="https://shreeraj.dev" target="_blank" rel="noopener noreferrer" className="social-link" title="Portfolio">
                    <Globe size={20} />
                  </a>
                </div>
              </div>
            </div>

            <div className="developer-card">
              <div className="developer-image">
                <div className="avatar-placeholder">
                  <span>SS</span>
                </div>
              </div>
              <div className="developer-info">
                <h3>Sonohar S</h3>
                <p className="developer-title">Frontend Developer</p>
                <div className="developer-links">
                  <a href="https://github.com/sonohar" target="_blank" rel="noopener noreferrer" className="social-link" title="GitHub">
                    <Github size={20} />
                  </a>
                  <a href="https://linkedin.com/in/sonohar" target="_blank" rel="noopener noreferrer" className="social-link" title="LinkedIn">
                    <Linkedin size={20} />
                  </a>
                  <a href="mailto:sonohar.dev@gmail.com" className="social-link" title="Email">
                    <Mail size={20} />
                  </a>
                </div>
              </div>
            </div>

            <div className="developer-card">
              <div className="developer-image">
                <div className="avatar-placeholder">
                  <span>AM</span>
                </div>
              </div>
              <div className="developer-info">
                <h3>Abhinash M</h3>
                <p className="developer-title">Backend Developer</p>
                <div className="developer-links">
                  <a href="https://github.com/abhinash" target="_blank" rel="noopener noreferrer" className="social-link" title="GitHub">
                    <Github size={20} />
                  </a>
                  <a href="https://linkedin.com/in/abhinash" target="_blank" rel="noopener noreferrer" className="social-link" title="LinkedIn">
                    <Linkedin size={20} />
                  </a>
                  <a href="mailto:abhinash.dev@gmail.com" className="social-link" title="Email">
                    <Mail size={20} />
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
