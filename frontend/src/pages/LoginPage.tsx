import { FormEvent, useState } from "react";
import { Navigate } from "react-router-dom";
import { useAuth } from "../services/auth";

export default function LoginPage() {
  const { token, login } = useAuth();
  const [email, setEmail] = useState("admin@example.com");
  const [password, setPassword] = useState("Admin123!");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  if (token) return <Navigate to="/" replace />;

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      await login(email, password);
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
          Sign in to search companies, run website intelligence, and export
          scored ERP leads.
        </p>
        <div className="stack">
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="Email"
            required
          />
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Password"
            required
          />
          {error && <p className="error">{error}</p>}
          <button className="btn btn-primary" type="submit" disabled={loading}>
            {loading ? "Signing in…" : "Enter workspace"}
          </button>
        </div>
        <p className="muted" style={{ marginTop: "1rem", fontSize: "0.85rem" }}>
          Default admin: admin@example.com / Admin123!
        </p>
      </form>
    </div>
  );
}
