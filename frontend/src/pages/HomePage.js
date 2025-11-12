import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import SiteFooter from '../components/SiteFooter';
import './HomePage.css';

function HomePage() {
  const navigate = useNavigate();
  const { isAuthenticated, displayName } = useAuth();

  const openDashboard = () => {
    navigate('/dashboard');
  };

  const openSignIn = () => {
    navigate('/login');
  };

  const openSignUp = () => {
    navigate('/login', { state: { openSignup: true } });
  };

  return (
    <div className="home">
      <header className="home__header">
        <div className="home__brand">
          <img
            src="/Cerevyn_logo_with_text-removebg-preview.png"
            alt="Cerevyn Solutions logo"
            className="home__logo"
          />
        </div>
        <nav className="home__nav">
          <button type="button" className="home__cta home__cta--ghost" onClick={openSignIn}>
            Sign In
          </button>
          <button type="button" className="home__cta home__cta--primary" onClick={openSignUp}>
            Sign Up
          </button>
        </nav>
      </header>

      <main className="home__main">
        <section className="home__hero">
          <div className="home__hero-copy">
            <h1 className="home__hero-title">CEREVAK</h1>
            <p className="home__hero-body">
            CEREVAK is a multilingual text-to-speech (TTS) platform designed to bridge linguistic diversity across India. It enables users to upload text or documents and convert them into natural-sounding voice outputs in 13 Indian languages and English.
            </p>
            <div className="home__actions">
              <button
                type="button"
                className="home__cta home__cta--primary"
                onClick={isAuthenticated ? openDashboard : openSignIn}
              >
                {isAuthenticated ? 'Enter Dashboard' : 'Get Started'}
              </button>
              <button type="button" className="home__cta home__cta--secondary" onClick={openSignUp}>
                {isAuthenticated ? `Hi, ${displayName}` : 'Create an account'}
              </button>
            </div>
          </div>
        </section>
      </main>

      <SiteFooter />
    </div>
  );
}

export default HomePage;


