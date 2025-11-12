import React, { useEffect, useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import SignupModal from '../components/SignupModal';
import { useAuth } from '../context/AuthContext';
import './AuthPage.css';

function LoginPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const { login, signup, isAuthenticated, loading: authLoading } = useAuth();
  const [form, setForm] = useState({ email: '', password: '' });
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showSignup, setShowSignup] = useState(false);

  useEffect(() => {
    if (isAuthenticated) {
      navigate('/dashboard', { replace: true });
    }
  }, [isAuthenticated, navigate]);

  useEffect(() => {
    if (location.state?.openSignup) {
      setShowSignup(true);
      navigate(location.pathname, { replace: true, state: {} });
    }
  }, [location, navigate]);

  const handleChange = (event) => {
    const { name, value } = event.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setStatus(null);
    setLoading(true);
    try {
      await login({
        email: form.email.trim().toLowerCase(),
        password: form.password,
      });
      setStatus({ type: 'success', message: 'Welcome back! Redirecting to dashboard…' });
      const redirectTo = location.state?.from?.pathname || '/dashboard';
      navigate(redirectTo, { replace: true });
    } catch (error) {
      setStatus({
        type: 'error',
        message: error.message || 'Unable to sign in. Please try again.',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSignup = async (payload) => {
    setStatus(null);
    setLoading(true);
    try {
      const { session, user } = await signup(payload);
      setShowSignup(false);
      if (session) {
        setStatus({ type: 'success', message: 'Account created! Redirecting to dashboard…' });
        navigate('/dashboard', { replace: true });
      } else {
        setStatus({
          type: 'success',
          message: `Account created for ${user?.email}. Please check your inbox to verify before signing in.`,
        });
      }
    } catch (error) {
      setStatus({
        type: 'error',
        message: error.message || 'Unable to create account. Please try again.',
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth">
      <header className="auth__header">
        <Link to="/" className="auth__brand auth__brand--center">
          <img src="/cerevyn_logo_with_text-removebg-preview.png" alt="Cerevyn Solutions logo" />
        </Link>
        <Link to="/" className="auth__link">
          Back to home
        </Link>
      </header>

      <main className="auth__main">
        <section className="auth__card auth__card--wide">
          <h1>Welcome to your Cerevak workspace</h1>
          <p>Sign in with your work email to access multilingual text-to-speech tools.</p>

          <form className="auth__form" onSubmit={handleSubmit}>
            <label>
              <span>Email</span>
              <input
                type="email"
                name="email"
                value={form.email}
                onChange={handleChange}
                placeholder="name@company.com"
                required
              />
            </label>

            <label>
              <span>Password</span>
              <input
                type="password"
                name="password"
                value={form.password}
                onChange={handleChange}
                placeholder="Enter your password"
                required
              />
            </label>

            <button type="submit" className="auth__submit" disabled={loading || authLoading}>
              {loading ? 'Signing in…' : 'Sign in'}
            </button>
          </form>

          {status && <div className={`auth__status auth__status--${status.type}`}>{status.message}</div>}

          <div className="auth__footer">
            <span>New to Cerevak?</span>
            <button type="button" className="auth__link-button" onClick={() => setShowSignup(true)}>
              Create an account
            </button>
          </div>
        </section>
      </main>

      <SignupModal
        isOpen={showSignup}
        onClose={() => setShowSignup(false)}
        onSignup={handleSignup}
        loading={loading || authLoading}
      />
    </div>
  );
}

export default LoginPage;


