import { useState } from "react";
import { useAuth } from "../context/AuthContext";
import { useToast } from "../context/ToastContext";

function FieldError({ msg }) {
  if (!msg) return null;
  return <div className="form-error">{msg}</div>;
}

export function LoginModal({ open, onClose, onSwitchToSignup }) {
  const { login } = useAuth();
  const { show } = useToast();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  if (!open) return null;

  const submit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const user = await login(email, password);
      show(`Welcome back, ${user.full_name.split(" ")[0]}!`, "success");
      onClose();
    } catch (err) {
      setError(err?.response?.data?.detail || "Login failed. Check your credentials.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={(e) => e.target.classList.contains("modal-overlay") && onClose()}>
      <div className="modal-card">
        <button className="modal-close" onClick={onClose}>✕</button>
        <div className="modal-logo">✈ PriceLens</div>
        <h2>Welcome back</h2>
        <form className="modal-form" onSubmit={submit}>
          <input className="modal-input" type="email" placeholder="Email address" value={email}
                 onChange={(e) => setEmail(e.target.value)} required />
          <input className="modal-input" type="password" placeholder="Password" value={password}
                 onChange={(e) => setPassword(e.target.value)} required />
          <FieldError msg={error} />
          <button className="btn-predict" type="submit" disabled={loading}>
            {loading ? <span className="loading-spinner" /> : null} {loading ? "Logging in..." : "Login"}
          </button>
        </form>
        <p className="modal-switch">No account? <a onClick={onSwitchToSignup}>Sign up free</a></p>
      </div>
    </div>
  );
}

export function SignupModal({ open, onClose, onSwitchToLogin }) {
  const { signup } = useAuth();
  const { show } = useToast();
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  if (!open) return null;

  const submit = async (e) => {
    e.preventDefault();
    setError("");
    if (password.length < 6) {
      setError("Password must be at least 6 characters.");
      return;
    }
    setLoading(true);
    try {
      const user = await signup(fullName, email, password);
      show(`Account created — welcome, ${user.full_name.split(" ")[0]}!`, "success");
      onClose();
    } catch (err) {
      setError(err?.response?.data?.detail || "Signup failed. Try a different email.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={(e) => e.target.classList.contains("modal-overlay") && onClose()}>
      <div className="modal-card">
        <button className="modal-close" onClick={onClose}>✕</button>
        <div className="modal-logo">✈ PriceLens</div>
        <h2>Create account</h2>
        <form className="modal-form" onSubmit={submit}>
          <input className="modal-input" type="text" placeholder="Full name" value={fullName}
                 onChange={(e) => setFullName(e.target.value)} required />
          <input className="modal-input" type="email" placeholder="Email address" value={email}
                 onChange={(e) => setEmail(e.target.value)} required />
          <input className="modal-input" type="password" placeholder="Create password (min 6 chars)" value={password}
                 onChange={(e) => setPassword(e.target.value)} required />
          <FieldError msg={error} />
          <button className="btn-predict" type="submit" disabled={loading}>
            {loading ? <span className="loading-spinner" /> : null} {loading ? "Creating..." : "Create Account"}
          </button>
        </form>
        <p className="modal-switch">Already have an account? <a onClick={onSwitchToLogin}>Login</a></p>
      </div>
    </div>
  );
}
