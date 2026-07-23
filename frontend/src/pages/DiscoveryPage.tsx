import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  api,
  type DiscoveryLead,
  type DiscoveryRun,
} from "../services/api";
import { useAuth } from "../services/auth";

export default function DiscoveryPage() {
  const { username, logout } = useAuth();
  const [offeringsCount, setOfferingsCount] = useState(0);
  const [agents, setAgents] = useState<
    Array<{ id: string; name: string; responsibility: string }>
  >([]);
  const [runs, setRuns] = useState<DiscoveryRun[]>([]);
  const [activeRun, setActiveRun] = useState<DiscoveryRun | null>(null);
  const [leads, setLeads] = useState<DiscoveryLead[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [running, setRunning] = useState(false);
  const [selectedLead, setSelectedLead] = useState<DiscoveryLead | null>(null);

  async function refreshRuns() {
    const list = await api.listDiscoveryRuns();
    setRuns(list);
    return list;
  }

  useEffect(() => {
    void (async () => {
      try {
        const [off, ag] = await Promise.all([
          api.listOfferings(),
          api.listDiscoveryAgents(),
        ]);
        setOfferingsCount(off.count);
        setAgents(ag.agents);
        const list = await refreshRuns();
        if (list[0]) {
          setActiveRun(list[0]);
          setLeads(await api.getDiscoveryLeads(list[0].id));
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load discovery");
      }
    })();
  }, []);

  async function startRun() {
    setRunning(true);
    setError(null);
    setSelectedLead(null);
    try {
      const run = await api.startDiscovery(100);
      setActiveRun(run);
      setLeads(await api.getDiscoveryLeads(run.id));
      await refreshRuns();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Discovery failed");
    } finally {
      setRunning(false);
    }
  }

  async function openRun(run: DiscoveryRun) {
    setActiveRun(run);
    setSelectedLead(null);
    setLeads(await api.getDiscoveryLeads(run.id));
  }

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="brand">
          <strong>SignalForge</strong>
          <span>
            ERP demand discovery · {username} · {offeringsCount} offerings tracked
          </span>
        </div>
        <div className="topbar-actions">
          <Link className="btn" to="/companies">
            Manual company analysis
          </Link>
          {activeRun && (
            <>
              <button
                className="btn"
                onClick={() => void api.exportDiscoveryCsv(activeRun.id)}
              >
                Export CSV
              </button>
              <button
                className="btn"
                onClick={() => void api.exportDiscoveryExcel(activeRun.id)}
              >
                Export Excel
              </button>
            </>
          )}
          <button className="btn" onClick={logout}>
            Sign out
          </button>
        </div>
      </header>

      <section className="panel">
        <div className="section-head">
          <h2>Find companies looking for ERP</h2>
          <button
            className="btn btn-primary"
            onClick={() => void startRun()}
            disabled={running}
          >
            {running ? "Discovering leads…" : "Start discovery (100 leads)"}
          </button>
        </div>
        <p className="muted">
          No manual ERP input needed. The system searches LinkedIn-indexed jobs
          and the public web for companies showing demand for major ERP
          solutions (IFS, SAP, Oracle, Infor, Dynamics, NetSuite, and more),
          then visits company websites for decision-maker contacts.
        </p>
        {error && <p className="error">{error}</p>}
        <div className="grid-3" style={{ marginTop: "0.75rem" }}>
          {agents.map((a) => (
            <div key={a.id} className="pill" style={{ display: "block", padding: "0.65rem" }}>
              <strong>
                Agent {a.id}. {a.name}
              </strong>
              <div className="muted" style={{ marginTop: "0.25rem" }}>
                {a.responsibility}
              </div>
            </div>
          ))}
        </div>
      </section>

      {(activeRun?.summary?.agent_trace || []).length > 0 && (
        <section className="panel">
          <h3>Last run — agent trace</h3>
          <ul className="factor-list">
            {(activeRun?.summary?.agent_trace || []).map((t) => (
              <li key={t.agent_name}>
                <strong>{t.agent_name}</strong>
                <div className="muted">
                  {t.status}
                  {t.duration_ms != null ? ` · ${t.duration_ms}ms` : ""}
                  {(t.notes || [])[0] ? ` · ${t.notes?.[0]}` : ""}
                </div>
              </li>
            ))}
          </ul>
        </section>
      )}

      <section className="panel">
        <div className="section-head">
          <h2>
            Leads{" "}
            {activeRun
              ? `(${leads.length}/${activeRun.target_lead_count}) · score sorted`
              : ""}
          </h2>
          <span className="pill">
            run status: {activeRun?.status || "none"}
          </span>
        </div>
        {runs.length > 1 && (
          <div style={{ display: "flex", gap: "0.4rem", flexWrap: "wrap", marginBottom: "0.75rem" }}>
            {runs.slice(0, 6).map((r) => (
              <button
                key={r.id}
                className="btn"
                onClick={() => void openRun(r)}
                style={{
                  borderColor:
                    activeRun?.id === r.id ? "var(--accent)" : undefined,
                }}
              >
                {r.leads_found} leads · {r.status}
              </button>
            ))}
          </div>
        )}
        <table className="table">
          <thead>
            <tr>
              <th>Score</th>
              <th>Company</th>
              <th>ERP demand</th>
              <th>Location</th>
              <th>Contacts</th>
            </tr>
          </thead>
          <tbody>
            {leads.map((lead) => (
              <tr key={lead.id} onClick={() => setSelectedLead(lead)}>
                <td className="score" style={{ fontSize: "1.1rem" }}>
                  {Number(lead.lead_score || 0).toFixed(0)}
                </td>
                <td>
                  <strong>{lead.company_name}</strong>
                  <div className="muted">
                    {lead.website || lead.linkedin_url || "—"}
                  </div>
                </td>
                <td>
                  {(lead.matched_offerings || []).slice(0, 3).join(", ") || "—"}
                </td>
                <td>{lead.location || "—"}</td>
                <td>{(lead.decision_makers || []).length}</td>
              </tr>
            ))}
            {!leads.length && (
              <tr>
                <td colSpan={5} className="muted">
                  No leads yet. Click <strong>Start discovery</strong> to find
                  companies looking for ERP solutions.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </section>

      {selectedLead && (
        <section className="panel">
          <div className="section-head">
            <h2>{selectedLead.company_name}</h2>
            <button className="btn" onClick={() => setSelectedLead(null)}>
              Close
            </button>
          </div>
          <p className="muted">{selectedLead.company_summary}</p>
          <p>
            <strong>Website:</strong>{" "}
            {selectedLead.website ? (
              <a href={selectedLead.website} target="_blank" rel="noreferrer">
                {selectedLead.website}
              </a>
            ) : (
              "—"
            )}
          </p>
          <p>
            <strong>LinkedIn:</strong>{" "}
            {selectedLead.linkedin_url ? (
              <a href={selectedLead.linkedin_url} target="_blank" rel="noreferrer">
                {selectedLead.linkedin_url}
              </a>
            ) : (
              "—"
            )}
          </p>
          <p>
            <strong>Matched offerings:</strong>{" "}
            {(selectedLead.matched_offerings || []).join(", ") || "—"}
          </p>
          <p>
            <strong>Why this lead:</strong> {selectedLead.score_explanation}
          </p>
          <h3>Decision makers</h3>
          <ul className="contact-list">
            {(selectedLead.decision_makers || []).map((p, idx) => (
              <li key={`${p.name}-${idx}`}>
                <strong>{p.name || "Unknown"}</strong>
                <div className="muted">
                  {p.designation || "—"}
                  {p.location ? ` · ${p.location}` : ""}
                </div>
                <div className="muted">
                  {p.email ? `Email: ${p.email}` : "Email: not public"}
                  {" · "}
                  {p.phone ? `Phone: ${p.phone}` : "Phone: not public"}
                </div>
                {p.linkedin_search && (
                  <a href={p.linkedin_search} target="_blank" rel="noreferrer">
                    LinkedIn search
                  </a>
                )}
              </li>
            ))}
            {!(selectedLead.decision_makers || []).length && (
              <li className="muted">No public decision-maker details found</li>
            )}
          </ul>
        </section>
      )}
    </div>
  );
}
