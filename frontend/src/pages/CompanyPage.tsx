import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api } from "../services/api";
import type { Company, IntelligenceBundle } from "../types/api";

export default function CompanyPage() {
  const { id = "" } = useParams();
  const [company, setCompany] = useState<Company | null>(null);
  const [intel, setIntel] = useState<IntelligenceBundle | null>(null);
  const [websitePreview, setWebsitePreview] = useState<Record<
    string,
    unknown
  > | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [running, setRunning] = useState(false);

  async function refresh() {
    const [c, i] = await Promise.all([
      api.getCompany(id),
      api.getIntelligence(id),
    ]);
    setCompany(c);
    setIntel(i);
  }

  useEffect(() => {
    void refresh().catch((err) =>
      setError(err instanceof Error ? err.message : "Load failed")
    );
  }, [id]);

  async function runAnalysis() {
    setRunning(true);
    setError(null);
    try {
      await api.runAnalysis(id);
      await refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Analysis failed");
    } finally {
      setRunning(false);
    }
  }

  async function previewWebsite() {
    if (!company?.website) return;
    setError(null);
    try {
      const result = await api.analyzeWebsite(company.website);
      setWebsitePreview(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Website analysis failed");
    }
  }

  const score = intel?.lead_score;
  const report = intel?.report;
  const wi = intel?.analysis?.website_intelligence as
    | Record<string, unknown>
    | undefined;
  const hiring = intel?.analysis?.hiring_analysis as
    | Record<string, unknown>
    | undefined;
  const opportunity = intel?.analysis?.erp_opportunity as
    | Record<string, unknown>
    | undefined;

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="brand">
          <strong>{company?.name || "Company"}</strong>
          <span>
            <Link to="/">← Back to search</Link>
            {company?.website ? ` · ${company.website}` : ""}
          </span>
        </div>
        <div className="topbar-actions">
          <button className="btn" onClick={() => void previewWebsite()}>
            Website analysis
          </button>
          <button
            className="btn btn-primary"
            onClick={() => void runAnalysis()}
            disabled={running}
          >
            {running ? "Running agents…" : "Run full analysis"}
          </button>
        </div>
      </header>

      {error && <p className="error">{error}</p>}

      <div className="grid-2">
        <section className="panel">
          <div className="section-head">
            <h2>Lead score</h2>
            <span className="pill">
              status: {intel?.analysis?.status || "none"}
            </span>
          </div>
          <div className="score">{score ? Number(score.score).toFixed(0) : "—"}</div>
          <p className="muted">{score?.explanation || "Run analysis to score this lead."}</p>
          <ul className="factor-list">
            {(score?.factors || []).map((f) => (
              <li key={f.name}>
                <strong>
                  {f.name} (+{f.points})
                </strong>
                <div className="muted">{f.reason}</div>
              </li>
            ))}
          </ul>
        </section>

        <section className="panel">
          <h2>Company details</h2>
          <p>
            <strong>Country:</strong> {company?.country || "—"}
          </p>
          <p>
            <strong>Industry:</strong>{" "}
            {(wi?.industry as string) || company?.industry || "—"}
          </p>
          <p>
            <strong>Employee size:</strong> {company?.employee_size || "—"}
          </p>
          <p>
            <strong>Revenue:</strong> {company?.revenue || "—"}
          </p>
          <p className="muted">{company?.description || "No description yet."}</p>
        </section>
      </div>

      <div className="grid-3" style={{ marginTop: "1rem" }}>
        <section className="panel">
          <h3>ERP detection</h3>
          <ul className="tech-list">
            {(
              (opportunity?.erp_systems as string[]) ||
              (wi?.erp_detected as string[]) ||
              []
            ).map((name) => (
              <li key={name}>{name}</li>
            ))}
            {!((opportunity?.erp_systems as string[]) || []).length &&
              !((wi?.erp_detected as string[]) || []).length && (
                <li className="muted">No ERP detected yet</li>
              )}
          </ul>
          <p className="muted" style={{ marginTop: "0.75rem" }}>
            Opportunities:{" "}
            {((opportunity?.opportunities as string[]) || []).join(", ") || "—"}
          </p>
        </section>

        <section className="panel">
          <h3>Technology stack</h3>
          <ul className="tech-list">
            {(intel?.technologies || []).map((t) => (
              <li key={t.id}>
                <strong>{t.name}</strong>
                <div className="muted">
                  {t.category}
                  {t.confidence ? ` · ${Number(t.confidence).toFixed(0)}%` : ""}
                </div>
              </li>
            ))}
            {!intel?.technologies?.length && (
              <li className="muted">No technologies yet</li>
            )}
          </ul>
        </section>

        <section className="panel">
          <h3>Hiring analysis</h3>
          <p className="score" style={{ fontSize: "1.6rem" }}>
            {hiring?.hiring_score != null ? String(hiring.hiring_score) : "—"}
          </p>
          <p className="muted">{(hiring?.summary as string) || "No hiring data"}</p>
          <div style={{ display: "flex", flexWrap: "wrap", gap: "0.4rem" }}>
            {Object.keys((hiring?.categories as object) || {}).map((key) => (
              <span className="pill" key={key}>
                {key}
              </span>
            ))}
          </div>
        </section>
      </div>

      <div className="grid-2" style={{ marginTop: "1rem" }}>
        <section className="panel">
          <h3>Decision makers</h3>
          <ul className="contact-list">
            {(intel?.contacts || []).map((c) => (
              <li key={c.id}>
                <strong>{c.full_name}</strong>
                <div className="muted">
                  {c.title || c.role_category}
                  {c.email ? ` · ${c.email}` : ""}
                </div>
                {c.profile_url && (
                  <a href={c.profile_url} target="_blank" rel="noreferrer">
                    Profile
                  </a>
                )}
              </li>
            ))}
            {!intel?.contacts?.length && (
              <li className="muted">No decision makers extracted</li>
            )}
          </ul>
        </section>

        <section className="panel">
          <h3>News</h3>
          <ul className="news-list">
            {(intel?.news || []).map((n) => (
              <li key={n.url}>
                <a href={n.url} target="_blank" rel="noreferrer">
                  {n.title || n.url}
                </a>
              </li>
            ))}
            {!intel?.news?.length && <li className="muted">No news links found</li>}
          </ul>
        </section>
      </div>

      <section className="panel" style={{ marginTop: "1rem" }}>
        <h3>Report</h3>
        {report ? (
          <>
            <p>
              <span className="pill">priority: {report.priority}</span>{" "}
              <span className="pill">
                deal: {report.estimated_deal_size_label || report.estimated_deal_size}
              </span>
            </p>
            <p>
              <strong>Executive summary.</strong> {report.executive_summary}
            </p>
            <p>
              <strong>Business opportunity.</strong> {report.business_opportunity}
            </p>
            <p>
              <strong>Why this prospect.</strong> {report.why_prospect}
            </p>
            <p>
              <strong>Recommended services.</strong>{" "}
              {(report.recommended_services || []).join(", ")}
            </p>
            <p>
              <strong>Next action.</strong> {report.next_action}
            </p>
          </>
        ) : (
          <p className="muted">Run full analysis to generate the sales report.</p>
        )}
      </section>

      {websitePreview && (
        <section className="panel" style={{ marginTop: "1rem" }}>
          <h3>Website analysis preview</h3>
          <p className="muted">
            pages: {String(websitePreview.pages_crawled)} · success:{" "}
            {String(websitePreview.success)} · engine:{" "}
            {String((websitePreview.metadata as { engine?: string })?.engine)}
          </p>
          <pre
            style={{
              whiteSpace: "pre-wrap",
              fontFamily: "var(--font-mono)",
              fontSize: "0.78rem",
              color: "var(--muted)",
              maxHeight: 240,
              overflow: "auto",
            }}
          >
            {String(websitePreview.combined_text || "").slice(0, 2500)}
          </pre>
        </section>
      )}
    </div>
  );
}
