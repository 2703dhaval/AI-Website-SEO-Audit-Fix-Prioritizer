export interface Audit {
  id: string;
  audit_name?: string;
  submitted_url: string;
  normalized_domain: string;
  status: 'queued' | 'running' | 'completed' | 'failed' | 'cancelled';
  configuration: {
    max_pages?: number;
    max_depth?: number;
    crawl_delay?: number;
    exclude_patterns?: string[];
  };
  started_at?: string;
  completed_at?: string;
  error_summary?: string;
  total_discovered_pages: number;
  total_crawled_pages: number;
  seo_health_score: number;
  scoring_version: string;
  crawl_policy_summary?: string;
  created_at: string;
}

export interface CrawledPage {
  id: string;
  audit_id: string;
  requested_url: string;
  final_url: string;
  canonical_url?: string;
  http_status: number;
  title?: string;
  meta_description?: string;
  h1_data?: string[];
  language?: string;
  robots_directives?: string;
  word_count: number;
  internal_link_count: number;
  external_link_count: number;
  response_time_ms: number;
  response_size_bytes: number;
  crawl_depth: number;
  indexability_status: string;
  created_at: string;
  issue_count?: number;
}

export interface IssueEvidence {
  id: string;
  issue_id: string;
  page_id?: string;
  page_url: string;
  observed_value?: string;
  expected_value?: string;
  evidence_snippet?: string;
  evidence_type: string;
  explanation?: string;
}

export interface SEOIssue {
  id: string;
  audit_id: string;
  issue_code: string;
  title: string;
  category: 'crawlability' | 'on_page' | 'internal_linking' | 'structured_data' | 'performance' | 'duplicates';
  severity: 'critical' | 'high' | 'medium' | 'low' | 'informational';
  priority_score: number;
  impact: number;
  confidence: number;
  estimated_effort: number;
  description: string;
  why_it_matters?: string;
  suggested_fix: string;
  example_fix?: string;
  priority_reason?: string;
  status: 'open' | 'in_progress' | 'resolved' | 'ignored';
  affected_page_count: number;
  created_at: string;
  evidences?: IssueEvidence[];
}

export interface AuditSummary {
  audit: Audit;
  health_score: number;
  total_pages: number;
  total_issues: number;
  severity_breakdown: Record<string, number>;
  category_breakdown: Record<string, number>;
  top_priority_fixes: {
    id: string;
    title: string;
    severity: string;
    priority_score: number;
    category: string;
    suggested_fix: string;
    affected_page_count: number;
    estimated_effort: number;
  }[];
  passed_checks_count: number;
  indexability_breakdown: Record<string, number>;
  http_status_breakdown: Record<string, number>;
}

export interface DashboardStats {
  total_audits: number;
  websites_audited: number;
  total_issues: number;
  critical_issues: number;
  high_issues: number;
  critical_and_high_issues: number;
  avg_health_score: number;
  recent_audits: Audit[];
  severity_distribution: Record<string, number>;
  category_distribution: Record<string, number>;
}

export interface ProgressResponse {
  audit_id: string;
  status: string;
  pages_discovered: number;
  pages_crawled: number;
  pages_remaining: number;
  current_stage: string;
  issues_detected_so_far: number;
  latest_event?: string;
}
