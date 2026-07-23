import { FormEvent, useEffect, useState } from "react";
import { Navigate } from "react-router-dom";
import { api } from "../services/api";
import { useAuth } from "../services/auth";

export default function LoginPage() {
  const { token, login } = useAuth();
  const [email, setEmail] = useState("admin@example.com");
  const [password, setPassword] = useState("Admin123!");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [apiStatus, setApiStatus] = useState<string>("checking API…");

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const ready = await api.ready();
        if (cancelled) return;
        setApiStatus(
          ready.admin_seeded
            ? `API ready · admin ${ready.admin_email}`
            : `API up but admin missing · ${ready.admin_email}`
        );
      } catch (err) {
        if (cancelled) return;
        setApiStatus(
          err instanceof Error
            ? `API error: ${err.message}`
            : "API unreachable"
        );
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  if (token) return <Navigate to="/" replace />;

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      await login(email.trim(), password);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="login-page">
      <form className="panel login-panel" onSubmit={onSubmit}>
        <p className="muted" style={{ margin: 0 }}>
          ERP opportunity desk
        </p>
        <h1>SignalForge</h1>
        <p className="muted">
          Sign in to discover companies looking for ERP solutions and export
          decision-maker contacts for outreach.
        </p>
        <p
          className="muted"
          style={{ fontSize: "0.8rem", fontFamily: "var(--font-mono)" }}
        >
          {apiStatus}
          <br />
          API base: {api.apiBase}
        </p>
        <div className="stack">
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="Email"
            required
            autoComplete="username"
          />
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Password"
            required
            autoComplete="current-password"
          />
          {error && <p className="error">{error}</p>}
          <button className="btn btn-primary" type="submit" disabled={loading}>
            {loading ? "Signing in…" : "Enter workspace"}
          </button>
        </div>
        <p className="muted" style={{ marginTop: "1rem", fontSize: "0.85rem" }}>
          Default admin: <strong>admin@example.com</strong> /{" "}
          <strong>Admin123!</strong>
        </p>
      </form>
    </div>
  );
}
