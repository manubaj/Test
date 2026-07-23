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
  const [statusNote, setStatusNote] = useState(
    "No discovery run yet — click Start discovery."
  );

  async function refreshRuns() {
    const list = await api.listDiscoveryRuns();
    setRuns(list);
    return list;
  }

  async function loadRunDetails(run: DiscoveryRun) {
    setActiveRun(run);
    const phase =
      (run.summary as { message?: string } | null | undefined)?.message ||
      run.status;
    setStatusNote(phase);
    if (run.status === "completed") {
      setLeads(await api.getDiscoveryLeads(run.id));
    } else if (run.status === "failed") {
      setLeads([]);
      setError(run.error_message || "Discovery run failed");
    } else {
      setLeads([]);
    }
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
          await loadRunDetails(list[0]);
          if (list[0].status === "running" || list[0].status === "pending") {
            setRunning(true);
          }
        } else {
          setStatusNote("No discovery run yet — click Start discovery.");
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load discovery");
        setStatusNote("Could not load discovery API.");
      }
    })();
  }, []);

  // Poll while a run is in progress
  useEffect(() => {
    if (!activeRun) return;
    if (activeRun.status !== "running" && activeRun.status !== "pending") return;

    const timer = window.setInterval(() => {
      void (async () => {
        try {
          const latest = await api.getDiscoveryRun(activeRun.id);
          setActiveRun(latest);
          const msg =
            (latest.summary as { message?: string } | null | undefined)?.message ||
            latest.status;
          setStatusNote(msg);
          if (latest.status === "completed") {
            setLeads(await api.getDiscoveryLeads(latest.id));
            setRunning(false);
            await refreshRuns();
          } else if (latest.status === "failed") {
            setError(latest.error_message || "Discovery failed");
            setRunning(false);
            await refreshRuns();
          }
        } catch (err) {
          setError(err instanceof Error ? err.message : "Polling failed");
        }
      })();
    }, 3000);

    return () => window.clearInterval(timer);
  }, [activeRun?.id, activeRun?.status]);

  async function startRun() {
    setRunning(true);
    setError(null);
    setSelectedLead(null);
    setLeads([]);
    setStatusNote("Starting discovery…");
    try {
      const run = await api.startDiscovery(100);
      setActiveRun(run);
      setStatusNote(
        (run.summary as { message?: string } | null | undefined)?.message ||
          "Discovery running in background…"
      );
      await refreshRuns();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Discovery failed");
      setRunning(false);
      setStatusNote("Start failed — see error above.");
    }
  }

  async function openRun(run: DiscoveryRun) {
    setError(null);
    setSelectedLead(null);
    await loadRunDetails(run);
    setRunning(run.status === "running" || run.status === "pending");
  }

  const statusLabel = activeRun?.status || "none";

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
          {activeRun?.status === "completed" && (
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
            {running ? "Discovery running…" : "Start discovery (100 leads)"}
          </button>
        </div>
        <p className="muted">
          No manual ERP input needed. Click <strong>Start discovery</strong> —
          status should change from <code>none</code> → <code>running</code> →{" "}
          <code>completed</code> (usually a few minutes).
        </p>
        {error && <p className="error">{error}</p>}
        <p className="muted" style={{ fontFamily: "var(--font-mono)" }}>
          {statusNote}
        </p>
        <div className="grid-3" style={{ marginTop: "0.75rem" }}>
          {agents.map((a) => (
            <div
              key={a.id}
              className="pill"
              style={{ display: "block", padding: "0.65rem" }}
            >
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
              ? `(${leads.length}/${activeRun.target_lead_count})`
              : ""}
          </h2>
          <span className="pill">run status: {statusLabel}</span>
        </div>
        {statusLabel === "none" && (
          <p className="muted">
            Status is <strong>none</strong> because no run exists yet. Press{" "}
            <strong>Start discovery (100 leads)</strong> above.
          </p>
        )}
        {statusLabel === "running" && (
          <p className="muted">
            Agents are working in the background. This page refreshes every 3
            seconds…
          </p>
        )}
        {runs.length > 0 && (
          <div
            style={{
              display: "flex",
              gap: "0.4rem",
              flexWrap: "wrap",
              marginBottom: "0.75rem",
            }}
          >
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
                  {statusLabel === "running"
                    ? "Leads will appear when the run completes…"
                    : "No leads yet. Click Start discovery."}
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
              <a
                href={selectedLead.linkedin_url}
                target="_blank"
                rel="noreferrer"
              >
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
