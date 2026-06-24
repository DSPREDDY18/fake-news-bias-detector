import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { authAPI } from '../services/api';

const AuthContext = createContext(null);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Check token on mount
  const checkAuth = useCallback(async () => {
    const token = localStorage.getItem('factlens_token');
    if (!token) {
      setLoading(false);
      return;
    }
    try {
      const response = await authAPI.getProfile();
      setUser(response.data.user || response.data);
    } catch (err) {
      localStorage.removeItem('factlens_token');
      localStorage.removeItem('factlens_user');
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  const login = async (email, password) => {
    setError(null);
    try {
      const response = await authAPI.login(email, password);
      const { access_token, user: userData } = response.data;
      localStorage.setItem('factlens_token', access_token);
      if (userData) {
        localStorage.setItem('factlens_user', JSON.stringify(userData));
        setUser(userData);
      } else {
        // Fetch profile if user data not returned with login
        const profileRes = await authAPI.getProfile();
        const profile = profileRes.data.user || profileRes.data;
        localStorage.setItem('factlens_user', JSON.stringify(profile));
        setUser(profile);
      }
      return { success: true };
    } catch (err) {
      const message = err.message || 'Login failed. Please try again.';
      setError(message);
      return { success: false, error: message };
    }
  };

  const register = async (username, email, password) => {
    setError(null);
    try {
      const response = await authAPI.register(username, email, password);
      const { access_token, user: userData } = response.data;
      if (access_token) {
        localStorage.setItem('factlens_token', access_token);
        if (userData) {
          localStorage.setItem('factlens_user', JSON.stringify(userData));
          setUser(userData);
        } else {
          const profileRes = await authAPI.getProfile();
          const profile = profileRes.data.user || profileRes.data;
          localStorage.setItem('factlens_user', JSON.stringify(profile));
          setUser(profile);
        }
      }
      return { success: true };
    } catch (err) {
      const message = err.message || 'Registration failed. Please try again.';
      setError(message);
      return { success: false, error: message };
    }
  };

  const logout = () => {
    localStorage.removeItem('factlens_token');
    localStorage.removeItem('factlens_user');
    setUser(null);
    setError(null);
  };

  const clearError = () => setError(null);

  const value = {
    user,
    loading,
    error,
    isAuthenticated: !!user,
    isAdmin: user?.role === 'admin',
    login,
    register,
    logout,
    clearError,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export default AuthContext;
