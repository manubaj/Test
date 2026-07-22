import type {
  Company,
  IntelligenceBundle,
  Page,
  TokenResponse,
} from "../types/api";

// Prefer same-origin `/api/v1` (nginx proxies to backend in Docker).
// Override with VITE_API_BASE_URL only for local Vite dev against a remote API.
const API_BASE = (import.meta.env.VITE_API_BASE_URL || "/api/v1").replace(
  /\/$/,
  ""
);

function authHeaders(): HeadersInit {
  const token = localStorage.getItem("access_token");
  const apiKey = localStorage.getItem("api_key");
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };
  if (token) headers.Authorization = `Bearer ${token}`;
  if (apiKey) headers["X-API-Key"] = apiKey;
  return headers;
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE}${path}`, {
      ...init,
      headers: {
        ...authHeaders(),
        ...(init?.headers || {}),
      },
    });
  } catch {
    throw new Error(
      `Cannot reach API at ${API_BASE}. Is the backend running? Try http://localhost:8000/api/v1/health`
    );
  }
  if (!response.ok) {
    let detail = response.statusText;
    try {
      const body = await response.json();
      detail = body.message || body.detail || detail;
    } catch {
      /* ignore */
    }
    throw new Error(detail);
  }
  if (response.status === 204) return undefined as T;
  const contentType = response.headers.get("content-type") || "";
  if (contentType.includes("application/json")) {
    return response.json();
  }
  return response.blob() as Promise<T>;
}

export const api = {
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
    const blob = (await request<Blob>("/export/csv")) as unknown as Blob;
    downloadBlob(blob, "leads.csv");
  },
  async exportExcel() {
    const blob = (await request<Blob>("/export/excel")) as unknown as Blob;
    downloadBlob(blob, "leads.xlsx");
  },
};

function downloadBlob(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}
