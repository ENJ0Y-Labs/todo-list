import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

function messageFor(error) {
  const messages = {
    EMAIL_ALREADY_REGISTERED: "That email is already registered.",
    USERNAME_ALREADY_REGISTERED: "That username is already taken.",
    VALIDATION_ERROR: error.message,
  };
  return messages[error?.code] || error?.message || "Unable to create your account.";
}

export default function Register() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({
    firstName: "", lastName: "", email: "", username: "", password: "", confirmPassword: "",
  });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const update = (field, value) => setForm((current) => ({ ...current, [field]: value }));

  async function submit(event) {
    event.preventDefault();
    setError("");

    if (form.password !== form.confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    setLoading(true);
    try {
      await register({
        email: form.email.trim(),
        password: form.password,
        username: form.username.trim(),
        fullname: [form.firstName.trim(), form.lastName.trim()].filter(Boolean).join(" "),
      });
      navigate("/dashboard", { replace: true });
    } catch (err) {
      setError(messageFor(err));
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="auth-page">
      <section className="auth-panel register-panel">
        <div className="brand auth-brand">
          <span className="brand-mark"><i className="fa-solid fa-check" /></span>
          Todo List
        </div>
        <span className="eyebrow">Get started</span>
        <h1>Create your account</h1>
        <p className="auth-subtitle">A simple workspace for getting things done.</p>

        <form className="auth-form" onSubmit={submit}>
          <div className="form-row">
            <label>First name<input required autoComplete="given-name" value={form.firstName} onChange={(e) => update("firstName", e.target.value)} /></label>
            <label>Last name<input required autoComplete="family-name" value={form.lastName} onChange={(e) => update("lastName", e.target.value)} /></label>
          </div>
          <label>Email<input required type="email" autoComplete="email" value={form.email} onChange={(e) => update("email", e.target.value)} /></label>
          <label>Username<input required autoComplete="username" value={form.username} onChange={(e) => update("username", e.target.value)} /></label>
          <div className="form-row">
            <label>Password<input required minLength="8" type="password" autoComplete="new-password" value={form.password} onChange={(e) => update("password", e.target.value)} /></label>
            <label>Confirm password<input required minLength="8" type="password" autoComplete="new-password" value={form.confirmPassword} onChange={(e) => update("confirmPassword", e.target.value)} /></label>
          </div>
          {error && <p className="form-error" role="alert">{error}</p>}
          <button className="primary-button auth-submit" disabled={loading}>
            {loading ? "Creating account..." : "Create account"}
          </button>
        </form>

        <p className="auth-switch">Already have an account? <Link to="/login">Sign in</Link></p>
      </section>
    </main>
  );
}
