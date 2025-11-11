import React, { useEffect, useState } from 'react';

const initialState = {
  fullName: '',
  email: '',
  password: '',
  confirmPassword: '',
};

function SignupModal({ isOpen, onClose, onSignup, loading = false }) {
  const [form, setForm] = useState(initialState);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!isOpen) {
      setForm(initialState);
      setError(null);
    }
  }, [isOpen]);

  if (!isOpen) {
    return null;
  }

  const handleChange = (event) => {
    const { name, value } = event.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    if (!form.fullName.trim() || !form.email.trim() || !form.password.trim()) {
      setError('Please fill in all required fields.');
      return;
    }

    if (form.password !== form.confirmPassword) {
      setError('Passwords do not match.');
      return;
    }

    setError(null);
    onSignup({
      fullName: form.fullName.trim(),
      email: form.email.trim().toLowerCase(),
      password: form.password,
    });
  };

  return (
    <div className="auth-modal">
      <div className="auth-modal__backdrop" role="button" tabIndex={-1} onClick={onClose} />
      <div className="auth-modal__content" role="dialog" aria-modal="true">
        <header className="auth-modal__header">
          <h2>Create your Cerevak account</h2>
          <button type="button" className="auth-modal__close" onClick={onClose} aria-label="Close signup modal">
            ×
          </button>
        </header>
        <form className="auth-modal__form" onSubmit={handleSubmit}>
          <label className="auth-modal__field">
            <span>Full name</span>
            <input
              type="text"
              name="fullName"
              value={form.fullName}
              onChange={handleChange}
              placeholder="Enter your full name"
              required
            />
          </label>
          <label className="auth-modal__field">
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
          <div className="auth-modal__field-group">
            <label className="auth-modal__field">
              <span>Password</span>
              <input
                type="password"
                name="password"
                value={form.password}
                onChange={handleChange}
                placeholder="Create a password"
                required
              />
            </label>
            <label className="auth-modal__field">
              <span>Confirm password</span>
              <input
                type="password"
                name="confirmPassword"
                value={form.confirmPassword}
                onChange={handleChange}
                placeholder="Repeat password"
                required
              />
            </label>
          </div>
          {error && <div className="auth-modal__error">{error}</div>}
          <div className="auth-modal__actions">
            <button type="button" className="auth-modal__secondary" onClick={onClose}>
              Cancel
            </button>
            <button type="submit" className="auth-modal__primary" disabled={loading}>
              {loading ? 'Creating account…' : 'Create account'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default SignupModal;


