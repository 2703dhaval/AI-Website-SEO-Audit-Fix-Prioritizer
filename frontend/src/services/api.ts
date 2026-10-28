import {
  Audit,
  CrawledPage,
  SEOIssue,
  AuditSummary,
  DashboardStats,
  ProgressResponse
} from '../types/api';

const API_BASE = '/api/v1';

async function fetchJson<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  });

  if (!res.ok) {
    let errorDetail = 'API request failed';
    try {
      const err = await res.json();
      errorDetail = err.detail || errorDetail;
    } catch {
      errorDetail = `HTTP ${res.status}: ${res.statusText}`;
    }
    throw new Error(errorDetail);
  }

  return res.json();
}

export const api = {
  // Dashboard & System
  getDashboardStats: () => fetchJson<DashboardStats>(`${API_BASE}/dashboard/stats`),
  getSampleReport: () => fetchJson<Audit>(`${API_BASE}/sample/sample-report`),
  getHealth: () => fetchJson<{ status: string; version: string; database: string }>(`/health`),

  // Audits CRUD
  listAudits: (skip = 0, limit = 50) =>
    fetchJson<Audit[]>(`${API_BASE}/audits?skip=${skip}&limit=${limit}`),

  createAudit: (data: {
    url: string;
    audit_name?: string;
    max_pages?: number;
    max_depth?: number;
    exclude_patterns?: string[];
    crawl_delay_seconds?: number;
  }) =>
    fetchJson<Audit>(`${API_BASE}/audits`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  getAudit: (auditId: string) => fetchJson<Audit>(`${API_BASE}/audits/${auditId}`),

  getAuditProgress: (auditId: string) =>
    fetchJson<ProgressResponse>(`${API_BASE}/audits/${auditId}/progress`),

  cancelAudit: (auditId: string) =>
    fetchJson<{ message: string; audit_id: string }>(`${API_BASE}/audits/${auditId}/cancel`, {
      method: 'POST',
    }),

  deleteAudit: async (auditId: string) => {
    const res = await fetch(`${API_BASE}/audits/${auditId}`, { method: 'DELETE' });
    if (!res.ok) throw new Error('Failed to delete audit');
  },

  getAuditSummary: (auditId: string) =>
    fetchJson<AuditSummary>(`${API_BASE}/audits/${auditId}/summary`),

  // Crawled Pages
  getCrawledPages: (
    auditId: string,
    params?: { page?: number; limit?: number; status_filter?: string; search?: string }
  ) => {
    const q = new URLSearchParams();
    if (params?.page) q.set('page', params.page.toString());
    if (params?.limit) q.set('limit', params.limit.toString());
    if (params?.status_filter) q.set('status_filter', params.status_filter);
    if (params?.search) q.set('search', params.search);
    return fetchJson<{
      items: CrawledPage[];
      total: number;
      page: number;
      limit: number;
      pages: number;
    }>(`${API_BASE}/audits/${auditId}/pages?${q.toString()}`);
  },

  // Issues & Fix Prioritization
  getAuditIssues: (
    auditId: string,
    params?: {
      page?: number;
      limit?: number;
      severity?: string;
      category?: string;
      status_filter?: string;
      search?: string;
      sort_by?: string;
      sort_dir?: string;
    }
  ) => {
    const q = new URLSearchParams();
    if (params?.page) q.set('page', params.page.toString());
    if (params?.limit) q.set('limit', params.limit.toString());
    if (params?.severity) q.set('severity', params.severity);
    if (params?.category) q.set('category', params.category);
    if (params?.status_filter) q.set('status_filter', params.status_filter);
    if (params?.search) q.set('search', params.search);
    if (params?.sort_by) q.set('sort_by', params.sort_by);
    if (params?.sort_dir) q.set('sort_dir', params.sort_dir);
    return fetchJson<{
      items: SEOIssue[];
      total: number;
      page: number;
      limit: number;
      pages: number;
    }>(`${API_BASE}/audits/${auditId}/issues?${q.toString()}`);
  },

  getIssueDetail: (auditId: string, issueId: string) =>
    fetchJson<SEOIssue>(`${API_BASE}/audits/${auditId}/issues/${issueId}`),

  updateIssueStatus: (auditId: string, issueId: string, status: string) =>
    fetchJson<SEOIssue>(`${API_BASE}/audits/${auditId}/issues/${issueId}`, {
      method: 'PATCH',
      body: JSON.stringify({ status }),
    }),

  // Comparisons
  compareAudits: (auditId1: string, auditId2: string) =>
    fetchJson<any>(`${API_BASE}/audits/${auditId1}/compare/${auditId2}`),

  // Export URLs
  getExportCsvUrl: (auditId: string) => `${API_BASE}/audits/${auditId}/export.csv`,
  getExportJsonUrl: (auditId: string) => `${API_BASE}/audits/${auditId}/export.json`,
  getReportPdfUrl: (auditId: string) => `${API_BASE}/audits/${auditId}/report.pdf`,
};
