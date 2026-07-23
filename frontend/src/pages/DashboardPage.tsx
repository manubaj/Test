import { FormEvent, useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api } from "../services/api";
import { useAuth } from "../services/auth";
import type { Company } from "../types/api";

export default function DashboardPage() {
  const { username, logout } = useAuth();
  const navigate = useNavigate();
  const [companies, setCompanies] = useState<Company[]>([]);
  const [q, setQ] = useState("");
  const [country, setCountry] = useState("");
  const [industry, setIndustry] = useState("");
  const [technology, setTechnology] = useState("");
  const [erp, setErp] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [name, setName] = useState("");
  const [website, setWebsite] = useState("");
  const [busy, setBusy] = useState(false);

  async function load() {
    setError(null);
    try {
      const page = await api.searchCompanies({
        q,
        country,
        industry,
        technology,
        erp,
        page: 1,
        page_size: 50,
      });
      setCompanies(page.items);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Search failed");
    }
  }

  useEffect(() => {
    void load();
  }, []);

  async function onCreate(e: FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError(null);
    try {
      const created = await api.createCompany({ name, website });
      setName("");
      setWebsite("");
      await load();
      navigate(`/companies/${created.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Create failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="brand">
          <strong>SignalForge</strong>
          <span>
            Manual company analysis · {username} ·{" "}
            <Link to="/">← Discovery home</Link>
          </span>
        </div>
        <div className="topbar-actions">
          <button className="btn" onClick={logout}>
            Sign out
          </button>
        </div>
      </header>

      <section className="panel">
        <h2>Company search</h2>
        <div className="search-row">
          <input
            placeholder="Name or website"
            value={q}
            onChange={(e) => setQ(e.target.value)}
          />
          <input
            placeholder="Country"
            value={country}
            onChange={(e) => setCountry(e.target.value)}
          />
          <input
            placeholder="Industry"
            value={industry}
            onChange={(e) => setIndustry(e.target.value)}
          />
          <input
            placeholder="Technology"
            value={technology}
            onChange={(e) => setTechnology(e.target.value)}
          />
          <input
            placeholder="ERP"
            value={erp}
            onChange={(e) => setErp(e.target.value)}
          />
          <button className="btn btn-primary" onClick={() => void load()}>
            Search
          </button>
        </div>
        {error && <p className="error">{error}</p>}
        <table className="table">
          <thead>
            <tr>
              <th>Company</th>
              <th>Website</th>
              <th>Country</th>
              <th>Industry</th>
              <th>Size</th>
            </tr>
          </thead>
          <tbody>
            {companies.map((c) => (
              <tr key={c.id} onClick={() => navigate(`/companies/${c.id}`)}>
                <td>{c.name}</td>
                <td className="muted">{c.website || "—"}</td>
                <td>{c.country || "—"}</td>
                <td>{c.industry || "—"}</td>
                <td>{c.employee_size || "—"}</td>
              </tr>
            ))}
            {!companies.length && (
              <tr>
                <td colSpan={5} className="muted">
                  No companies yet. Add one below to run analysis.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </section>

      <section className="panel">
        <h2>Add company</h2>
        <form className="search-row" onSubmit={onCreate}>
          <input
            placeholder="Company name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
          />
          <input
            placeholder="https://company.example"
            value={website}
            onChange={(e) => setWebsite(e.target.value)}
            style={{ gridColumn: "span 3" }}
          />
          <button className="btn btn-primary" disabled={busy}>
            {busy ? "Saving…" : "Create & open"}
          </button>
        </form>
      </section>
    </div>
  );
}
