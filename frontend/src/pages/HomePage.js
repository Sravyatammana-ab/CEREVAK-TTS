import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import './HomePage.css';

function HomePage() {
  const navigate = useNavigate();
  const { isAuthenticated, user } = useAuth();

  const handleGetStarted = () => {
    navigate(isAuthenticated ? '/dashboard' : '/login');
  };

  return (
    <div className="home">
      <header className="home__header">
        <div className="home__brand">
          <img src="/cerevyn_logo.png" alt="Cerevyn Solutions logo" className="home__logo" />
          <span className="home__brand-name">Cerevak</span>
        </div>
        <nav className="home__nav">
          <Link to="/login" className="home__link">
            Login
          </Link>
          <button type="button" className="home__cta" onClick={handleGetStarted}>
            {isAuthenticated ? 'Go to Dashboard' : 'Get Started'}
          </button>
        </nav>
      </header>

      <main className="home__main">
        <section className="home__hero">
          <div className="home__hero-text">
            <h1>Break language barriers with lifelike voice translations.</h1>
            <p>
              Cerevak empowers teams to convert text into expressive speech across languages. Build inclusive
              experiences, localize content, and scale your voice strategy with one powerful interface.
            </p>
            <div className="home__actions">
              <button type="button" className="home__cta home__cta--primary" onClick={handleGetStarted}>
                {isAuthenticated ? 'Return to Dashboard' : 'Try Cerevak'}
              </button>
              <Link to="/login" className="home__cta home__cta--secondary">
                {isAuthenticated ? `Logged in as ${user?.displayName}` : 'Sign in to explore'}
              </Link>
            </div>
          </div>
          <div className="home__hero-card">
            <h2>What you can do:</h2>
            <ul>
              <li>Translate any script instantly into natural speech</li>
              <li>Switch between voices and control pitch, tone, and language</li>
              <li>Download audio files for podcasts, IVRs, and training content</li>
            </ul>
          </div>
        </section>

        <section className="home__features">
          <article className="home__feature-card">
            <h3>No engineering heavy-lift</h3>
            <p>
              Paste text or upload documents and let Cerevak handle detection, translation, and voice synthesis in a
              single flow.
            </p>
          </article>
          <article className="home__feature-card">
            <h3>Production-ready quality</h3>
            <p>
              Fine-tune delivery with pitch control, choose voice personas, and export clean audio files in seconds.
            </p>
          </article>
          <article className="home__feature-card">
            <h3>Secure team workspace</h3>
            <p>
              Dedicated login ensures your projects, voices, and audio assets stay in one protected environment.
            </p>
          </article>
        </section>

        <section className="home__callout">
          <h2>Ready to experience the Cerevak dashboard?</h2>
          <p>Sign in to start generating multilingual voiceovers with your team today.</p>
          <button type="button" className="home__cta home__cta--primary" onClick={handleGetStarted}>
            {isAuthenticated ? 'Open Dashboard' : 'Login to Continue'}
          </button>
        </section>
      </main>

      <footer className="home__footer">
        <span>© {new Date().getFullYear()} Cerevyn Solutions. All rights reserved.</span>
      </footer>
    </div>
  );
}

export default HomePage;


