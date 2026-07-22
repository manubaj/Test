import type {
  Company,
  IntelligenceBundle,
  Page,
  TokenResponse,
} from "../types/api";

// Prefer same-origin `/api/v1` (nginx / Vite proxy → backend).
const API_BASE = (import.meta.env.VITE_API_BASE_URL || "/api/v1").replace(
  /\/$/,
  ""
);

function authHeaders(): HeadersInit {
  const token = localStorage.getItem("access_token");
  const apiKey = localStorage.getItem("api_key");
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    Accept: "application/json",
  };
  if (token) headers.Authorization = `Bearer ${token}`;
  if (apiKey) headers["X-API-Key"] = apiKey;
  return headers;
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const url = `${API_BASE}${path}`;
  let response: Response;
  try {
    response = await fetch(url, {
      ...init,
      headers: {
        ...authHeaders(),
        ...(init?.headers || {}),
      },
    });
  } catch {
    throw new Error(
      `Cannot reach API (${url}). Check: curl http://127.0.0.1:8000/api/v1/ready`
    );
  }

  const contentType = response.headers.get("content-type") || "";
  if (!response.ok) {
    let detail = `${response.status} ${response.statusText}`;
    if (contentType.includes("application/json")) {
      try {
        const body = await response.json();
        detail = body.message || body.detail || detail;
      } catch {
        /* ignore */
      }
    } else {
      detail = `${detail} (API returned non-JSON — is the backend up? URL=${url})`;
    }
    throw new Error(detail);
  }

  if (response.status === 204) return undefined as T;

  if (!contentType.includes("application/json")) {
    // Likely Vite/nginx HTML fallback instead of the API
    throw new Error(
      `API returned HTML instead of JSON from ${url}. Rebuild frontend or start backend on :8000.`
    );
  }

  return response.json();
}

export const api = {
  apiBase: API_BASE,
  async ready() {
    return request<{
      status: string;
      admin_seeded: boolean;
      admin_email: string;
    }>("/ready");
  },
  async loginHelp() {
    return request<{
      email: string;
      password: string;
      admin_exists: boolean;
    }>("/auth/login-help");
  },
  login(email: string, password: string) {
    return request<TokenResponse>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });
  },
  searchCompanies(params: Record<string, string | number | undefined>) {
    const qs = new URLSearchParams();
    Object.entries(params).forEach(([k, v]) => {
      if (v !== undefined && v !== "") qs.set(k, String(v));
    });
    return request<Page<Company>>(`/companies?${qs.toString()}`);
  },
  createCompany(payload: Partial<Company> & { name: string }) {
    return request<Company>("/companies", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },
  getCompany(id: string) {
    return request<Company>(`/companies/${id}`);
  },
  runAnalysis(companyId: string) {
    return request(`/analysis`, {
      method: "POST",
      body: JSON.stringify({ company_id: companyId, run_async: false }),
    });
  },
  getIntelligence(companyId: string) {
    return request<IntelligenceBundle>(`/companies/${companyId}/intelligence`);
  },
  analyzeWebsite(url: string) {
    return request<Record<string, unknown>>(
      `/website/analyze?url=${encodeURIComponent(url)}`,
      { method: "POST" }
    );
  },
  async exportCsv() {
    const blob = (await requestBlob("/export/csv")) as Blob;
    downloadBlob(blob, "leads.csv");
  },
  async exportExcel() {
    const blob = (await requestBlob("/export/excel")) as Blob;
    downloadBlob(blob, "leads.xlsx");
  },
};

async function requestBlob(path: string): Promise<Blob> {
  const url = `${API_BASE}${path}`;
  const response = await fetch(url, { headers: authHeaders() });
  if (!response.ok) {
    throw new Error(`Export failed (${response.status})`);
  }
  return response.blob();
}

function downloadBlob(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}
