import { Routes, Route } from "react-router-dom";
import { useState } from "react";

import { AuthProvider } from "./context/AuthContext";
import { ToastProvider } from "./context/ToastContext";

import Navbar from "./components/Navbar";
import { LoginModal, SignupModal } from "./components/AuthModals";
import ChatAssistant from "./components/ChatAssistant";

import Home from "./pages/Home";
import Analytics from "./pages/Analytics";
import Dashboard from "./pages/Dashboard";

function Footer() {
  return (
    <footer className="footer">
      <div className="footer-inner">
        <div className="footer-brand">
          <span className="logo-icon">✈</span>
          <span className="logo-text">Price<span className="logo-accent">Lens</span></span>
          <p>See through the price. Travel smarter.</p>
        </div>
        <div className="footer-links">
          <div className="footer-col">
            <h5>Features</h5>
            <a href="/">Flight Search</a>
            <a href="/analytics">Analytics</a>
            <a href="/dashboard?tab=predictor">Predictor</a>
          </div>
          <div className="footer-col">
            <h5>Tools</h5>
            <a href="/dashboard?tab=budget">Budget Planner</a>
            <a href="/dashboard?tab=alerts">Smart Alerts</a>
          </div>
          <div className="footer-col">
            <h5>Project</h5>
            <a href="https://github.com" target="_blank" rel="noreferrer">GitHub</a>
          </div>
        </div>
      </div>
      <div className="footer-bottom">
        <p>© 2026 PriceLens · MCA Project · React + FastAPI + XGBoost + SHAP</p>
      </div>
    </footer>
  );
}

export default function App() {
  const [loginOpen, setLoginOpen] = useState(false);
  const [signupOpen, setSignupOpen] = useState(false);

  return (
    <AuthProvider>
      <ToastProvider>
        <Navbar onOpenLogin={() => setLoginOpen(true)} onOpenSignup={() => setSignupOpen(true)} />

        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/analytics" element={<Analytics />} />
          <Route path="/dashboard" element={<Dashboard />} />
        </Routes>

        <Footer />

        <LoginModal
          open={loginOpen}
          onClose={() => setLoginOpen(false)}
          onSwitchToSignup={() => { setLoginOpen(false); setSignupOpen(true); }}
        />
        <SignupModal
          open={signupOpen}
          onClose={() => setSignupOpen(false)}
          onSwitchToLogin={() => { setSignupOpen(false); setLoginOpen(true); }}
        />

        <ChatAssistant />
      </ToastProvider>
    </AuthProvider>
  );
}
