import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

function messageFor(error) {
  const messages = {
    INVALID_CREDENTIALS: "Incorrect username or password.",
    ACCOUNT_SUSPENDED: "This account is suspended.",
    VALIDATION_ERROR: error.message,
  };
  return messages[error?.code] || error?.message || "Unable to sign in.";
}

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ username: "", password: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const update = (field, value) => setForm((current) => ({ ...current, [field]: value }));

  async function submit(event) {
    event.preventDefault();
    setError("");
    setLoading(true);

    try {
      await login({ username: form.username.trim(), password: form.password });
      navigate("/dashboard", { replace: true });
    } catch (err) {
      setError(messageFor(err));
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="auth-page">
      <section className="auth-panel">
        <div className="brand auth-brand">
          <span className="brand-mark"><i className="fa-solid fa-check" /></span>
          Todo List
        </div>
        <span className="eyebrow">Your workspace</span>
        <h1>Welcome back</h1>
        <p className="auth-subtitle">Sign in to manage your tasks.</p>

        <form className="auth-form" onSubmit={submit}>
          <label>
            Username
            <input required autoComplete="username" value={form.username} onChange={(e) => update("username", e.target.value)} />
          </label>
          <label>
            Password
            <input required type="password" autoComplete="current-password" value={form.password} onChange={(e) => update("password", e.target.value)} />
          </label>
          {error && <p className="form-error" role="alert">{error}</p>}
          <button className="primary-button auth-submit" disabled={loading}>
            {loading ? "Signing in..." : "Sign in"}
          </button>
        </form>

        <p className="auth-switch">Don't have an account? <Link to="/register">Create one</Link></p>
      </section>
    </main>
  );
}
