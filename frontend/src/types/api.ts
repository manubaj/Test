export type UserRole = "admin" | "analyst" | "viewer";

export interface TokenResponse {
  access_token: string;
  token_type: string;
  role: UserRole;
  user_id: string;
  username: string;
}

export interface Company {
  id: string;
  name: string;
  website?: string | null;
  country?: string | null;
  industry?: string | null;
  revenue?: string | null;
  employee_size?: string | null;
  description?: string | null;
  is_active: boolean;
}

export interface Page<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}

export interface Contact {
  id: string;
  full_name: string;
  title?: string | null;
  role_category: string;
  email?: string | null;
  profile_url?: string | null;
}

export interface Technology {
  id: string;
  name: string;
  category: string;
  confidence?: string | null;
  evidence?: string | null;
}

export interface LeadScore {
  id: string;
  score: string;
  explanation: string;
  factors: Array<{ name: string; points: number; reason: string }>;
}

export interface Report {
  id: string;
  executive_summary: string;
  business_opportunity: string;
  why_prospect: string;
  recommended_services: string[];
  estimated_deal_size?: string | null;
  estimated_deal_size_label?: string | null;
  priority: string;
  next_action: string;
}

export interface Analysis {
  id: string;
  company_id: string;
  status: string;
  website_intelligence?: Record<string, unknown> | null;
  erp_opportunity?: Record<string, unknown> | null;
  hiring_analysis?: Record<string, unknown> | null;
  overall_confidence?: string | null;
  error_message?: string | null;
}

export interface IntelligenceBundle {
  company_id: string;
  analysis?: Analysis | null;
  contacts: Contact[];
  technologies: Technology[];
  lead_score?: LeadScore | null;
  report?: Report | null;
  news: Array<{ title: string; url: string }>;
}
