import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';

const RegisterForm = ({ onSwitch, onSuccess }) => {
  const { register } = useAuth();
  const [form, setForm] = useState({ username: '', email: '', password: '', confirmPassword: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
    setError('');
  };

  const validate = () => {
    if (!form.username || form.username.length < 3) return 'Username must be at least 3 characters';
    if (!form.email || !/\S+@\S+\.\S+/.test(form.email)) return 'Please enter a valid email';
    if (!form.password || form.password.length < 8) return 'Password must be at least 8 characters';
    if (!/(?=.*[A-Za-z])(?=.*\d)/.test(form.password)) return 'Password must contain a letter and a number';
    if (form.password !== form.confirmPassword) return 'Passwords do not match';
    return null;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const validationError = validate();
    if (validationError) { setError(validationError); return; }
    setLoading(true);
    try {
      await register(form.username, form.email, form.password);
      onSuccess && onSuccess();
    } catch (err) {
      setError(err.response?.data?.error?.message || err.response?.data?.message || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="glass-card p-4" style={{ maxWidth: 420, margin: '0 auto' }}>
      <h3 className="gradient-text text-center mb-4">Create Account</h3>
      {error && <div className="alert alert-danger py-2 small">{error}</div>}
      <form onSubmit={handleSubmit}>
        <div className="mb-3">
          <label className="form-label text-secondary small">Username</label>
          <input type="text" name="username" className="form-control dark-input" placeholder="johndoe"
            value={form.username} onChange={handleChange} required />
        </div>
        <div className="mb-3">
          <label className="form-label text-secondary small">Email</label>
          <input type="email" name="email" className="form-control dark-input" placeholder="john@example.com"
            value={form.email} onChange={handleChange} required />
        </div>
        <div className="mb-3">
          <label className="form-label text-secondary small">Password</label>
          <input type="password" name="password" className="form-control dark-input" placeholder="Min 8 characters"
            value={form.password} onChange={handleChange} required />
        </div>
        <div className="mb-3">
          <label className="form-label text-secondary small">Confirm Password</label>
          <input type="password" name="confirmPassword" className="form-control dark-input" placeholder="Repeat password"
            value={form.confirmPassword} onChange={handleChange} required />
        </div>
        <button type="submit" className="btn btn-primary-gradient w-100" disabled={loading}>
          {loading ? <span className="loading-spinner-sm me-2" /> : null}
          {loading ? 'Creating Account...' : 'Register'}
        </button>
      </form>
      <p className="text-center text-secondary small mt-3 mb-0">
        Already have an account?{' '}
        <button className="btn btn-link p-0 text-accent" onClick={onSwitch}>Sign In</button>
      </p>
    </div>
  );
};

export default RegisterForm;
