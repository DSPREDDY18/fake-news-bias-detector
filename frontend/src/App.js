import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import Navbar from './components/Navbar';
import ProtectedRoute from './components/ProtectedRoute';
import Home from './pages/Home';
import AnalyzeArticle from './pages/AnalyzeArticle';
import AnalysisHistory from './pages/AnalysisHistory';
import Reports from './pages/Reports';
import AdminDashboard from './pages/AdminDashboard';
import './App.css';

function App() {
  return (
    <AuthProvider>
      <div className="App">
        <Navbar />
        <main style={{ paddingTop: '70px', minHeight: '100vh' }}>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/analyze" element={<AnalyzeArticle />} />
            <Route path="/history" element={<AnalysisHistory />} />
            <Route path="/reports" element={
              <ProtectedRoute><Reports /></ProtectedRoute>
            } />
            <Route path="/admin" element={
              <ProtectedRoute adminOnly><AdminDashboard /></ProtectedRoute>
            } />
          </Routes>
        </main>
        <footer className="text-center py-4" style={{ borderTop: '1px solid var(--border-glass)' }}>
          <p className="text-secondary small mb-0">
            © 2025 FactLens AI — Fake News Bias Detection System. Built with ❤️ and AI.
          </p>
        </footer>
      </div>
    </AuthProvider>
  );
}

export default App;
