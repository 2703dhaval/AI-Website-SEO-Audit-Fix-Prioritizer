import React, { useEffect, useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import {
  FileText,
  Download,
  Filter,
  Search,
  ExternalLink,
  Layers,
  ArrowUpRight,
  ShieldCheck,
  CheckCircle2,
  Trash2,
  RotateCw,
  Sparkles,
  SlidersHorizontal,
  ChevronRight
} from 'lucide-react';
import { api } from '../services/api';
import { AuditSummary, SEOIssue, Audit } from '../types/api';
import { ScoreBadge } from '../components/ScoreBadge';
import { SeverityBadge } from '../components/SeverityBadge';
import { StatusBadge } from '../components/StatusBadge';
import { IssueDrawer } from '../components/IssueDrawer';
import { LoadingSkeleton } from '../components/LoadingSkeleton';

export const AuditResultsPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [summary, setSummary] = useState<AuditSummary | null>(null);
  const [issues, setIssues] = useState<SEOIssue[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [selectedSeverity, setSelectedSeverity] = useState<string>('');
  const [selectedCategory, setSelectedCategory] = useState<string>('');
  const [selectedStatus, setSelectedStatus] = useState<string>('');
  const [searchQuery, setSearchQuery] = useState<string>('');

  // Selected issue for detail drawer
  const [activeIssue, setActiveIssue] = useState<SEOIssue | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    if (id) {
      loadAuditData();
    }
  }, [id, selectedSeverity, selectedCategory, selectedStatus, searchQuery]);

  const loadAuditData = async () => {
    if (!id) return;
    try {
      setLoading(true);
      setError(null);

      const [sumData, issData] = await Promise.all([
        api.getAuditSummary(id),
        api.getAuditIssues(id, {
          severity: selectedSeverity || undefined,
          category: selectedCategory || undefined,
          status_filter: selectedStatus || undefined,
          search: searchQuery || undefined,
          limit: 100,
        }),
      ]);

      setSummary(sumData);
      setIssues(issData.items);
    } catch (err: any) {
      setError(err.message || 'Failed to load audit results');
    } finally {
      setLoading(false);
    }
  };

  const handleStatusChange = async (issueId: string, newStatus: string) => {
    if (!id) return;
    try {
      const updated = await api.updateIssueStatus(id, issueId, newStatus);
      setIssues((prev) => prev.map((item) => (item.id === issueId ? updated : item)));
      if (activeIssue?.id === issueId) {
        setActiveIssue(updated);
      }
    } catch (err) {
      console.error('Failed to update status', err);
    }
  };

  const handleDeleteAudit = async () => {
    if (!id) return;
    if (window.confirm('Are you sure you want to delete this audit record? All associated crawled pages and findings will be permanently removed.')) {
      try {
        await api.deleteAudit(id);
        navigate('/dashboard');
      } catch (err: any) {
        alert(err.message || 'Failed to delete audit');
      }
    }
  };

  if (loading && !summary) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
        <div className="h-10 bg-slate-200 rounded animate-pulse w-64" />
        <div className="h-32 bg-slate-200 rounded-xl animate-pulse" />
        <LoadingSkeleton rows={8} />
      </div>
    );
  }

  if (error || !summary) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 text-center">
        <h2 className="text-xl font-bold text-slate-900">Audit Not Found</h2>
        <p className="text-sm text-slate-500 mt-2">{error || 'Unable to locate specified audit record.'}</p>
        <Link
          to="/dashboard"
          className="mt-5 inline-flex items-center gap-2 px-4 py-2 bg-brand-900 text-white rounded-lg text-xs font-semibold"
        >
          Return to Dashboard
        </Link>
      </div>
    );
  }

  const { audit, health_score, severity_breakdown, category_breakdown } = summary;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Top Banner / Audit Header */}
      <div className="bg-white rounded-2xl border border-slate-200/90 p-6 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div className="space-y-1.5">
          <div className="flex flex-wrap items-center gap-2.5">
            <h1 className="text-2xl font-bold text-slate-900 tracking-tight">
              {audit.normalized_domain}
            </h1>
            <span
              className={`px-2.5 py-0.5 rounded text-xs font-medium capitalize ${
                audit.status === 'completed'
                  ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                  : 'bg-slate-100 text-slate-600'
              }`}
            >
              {audit.status}
            </span>
            <span className="text-xs text-slate-400 font-mono">ID: {audit.id.slice(0, 8)}</span>
          </div>

          <div className="text-xs text-slate-500 flex flex-wrap items-center gap-x-4 gap-y-1">
            <span className="font-mono text-slate-700">{audit.submitted_url}</span>
            <span>• Audited {new Date(audit.created_at).toLocaleString()}</span>
            <span>• Scored with {audit.scoring_version}</span>
          </div>

          {audit.crawl_policy_summary && (
            <p className="text-[11px] text-slate-500 bg-slate-50 px-2.5 py-1 rounded border border-slate-200/60 inline-block font-mono">
              Policy: {audit.crawl_policy_summary}
            </p>
          )}
        </div>

        {/* Health Score Card */}
        <div className="flex items-center gap-6 bg-slate-50/70 border border-slate-200/70 p-4 rounded-xl">
          <div>
            <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider block mb-1">
              SEO Health Score
            </span>
            <ScoreBadge score={health_score} size="lg" />
          </div>

          {/* Quick Exports and Actions */}
          <div className="border-l border-slate-200 pl-4 space-y-1.5 text-xs">
            <a
              href={api.getReportPdfUrl(audit.id)}
              download
              className="flex items-center gap-1.5 text-slate-700 hover:text-brand-900 font-medium py-0.5"
            >
              <Download className="w-3.5 h-3.5 text-brand-700" />
              Download PDF Report
            </a>
            <a
              href={api.getExportCsvUrl(audit.id)}
              download
              className="flex items-center gap-1.5 text-slate-700 hover:text-brand-900 font-medium py-0.5"
            >
              <FileText className="w-3.5 h-3.5 text-emerald-700" />
              Export CSV Fix List
            </a>
            <button
              onClick={handleDeleteAudit}
              className="flex items-center gap-1.5 text-rose-600 hover:text-rose-800 font-medium py-0.5"
            >
              <Trash2 className="w-3.5 h-3.5" />
              Delete Audit
            </button>
          </div>
        </div>
      </div>

      {/* Audit KPI Overview Strip */}
      <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-6 gap-3">
        <div className="bg-white p-3.5 rounded-xl border border-slate-200 text-center">
          <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider block">
            Pages Crawled
          </span>
          <span className="text-xl font-bold font-mono text-slate-900 mt-0.5 block">
            {summary.total_pages}
          </span>
          <Link
            to={`/audits/${audit.id}/pages`}
            className="text-[10px] text-brand-700 hover:underline font-medium inline-flex items-center gap-0.5 mt-1"
          >
            Inspect Pages <ChevronRight className="w-3 h-3" />
          </Link>
        </div>

        <div className="bg-white p-3.5 rounded-xl border border-slate-200 text-center">
          <span className="text-[10px] font-semibold text-rose-600 uppercase tracking-wider block">
            Critical Issues
          </span>
          <span className="text-xl font-bold font-mono text-rose-700 mt-0.5 block">
            {severity_breakdown['critical'] || 0}
          </span>
          <span className="text-[10px] text-slate-400">Immediate action</span>
        </div>

        <div className="bg-white p-3.5 rounded-xl border border-slate-200 text-center">
          <span className="text-[10px] font-semibold text-orange-600 uppercase tracking-wider block">
            High Severity
          </span>
          <span className="text-xl font-bold font-mono text-orange-700 mt-0.5 block">
            {severity_breakdown['high'] || 0}
          </span>
          <span className="text-[10px] text-slate-400">Significant impact</span>
        </div>

        <div className="bg-white p-3.5 rounded-xl border border-slate-200 text-center">
          <span className="text-[10px] font-semibold text-amber-600 uppercase tracking-wider block">
            Medium Severity
          </span>
          <span className="text-xl font-bold font-mono text-amber-700 mt-0.5 block">
            {severity_breakdown['medium'] || 0}
          </span>
          <span className="text-[10px] text-slate-400">Moderate impact</span>
        </div>

        <div className="bg-white p-3.5 rounded-xl border border-slate-200 text-center">
          <span className="text-[10px] font-semibold text-blue-600 uppercase tracking-wider block">
            Low / Advisory
          </span>
          <span className="text-xl font-bold font-mono text-blue-700 mt-0.5 block">
            {(severity_breakdown['low'] || 0) + (severity_breakdown['informational'] || 0)}
          </span>
          <span className="text-[10px] text-slate-400">Optimization notes</span>
        </div>

        <div className="bg-white p-3.5 rounded-xl border border-slate-200 text-center">
          <span className="text-[10px] font-semibold text-emerald-600 uppercase tracking-wider block">
            Passed Checks
          </span>
          <span className="text-xl font-bold font-mono text-emerald-700 mt-0.5 block">
            {summary.passed_checks_count}
          </span>
          <span className="text-[10px] text-slate-400">Zero defect rules</span>
        </div>
      </div>

      {/* Filter and Prioritized Fixes Header */}
      <div className="space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h2 className="text-lg font-bold text-slate-900 tracking-tight">
              Prioritized Fix Roadmap ({issues.length} Findings)
            </h2>
            <p className="text-xs text-slate-500 mt-0.5">
              Ranked by deterministic score: <i>100 × (0.45×Impact + 0.30×Scope + 0.25×Confidence) × (1 - 0.15×Effort)</i>
            </p>
          </div>

          <Link
            to={`/audits/${audit.id}/pages`}
            className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-700 bg-white hover:bg-slate-50 border border-slate-300 px-3 py-2 rounded-lg transition-colors"
          >
            <Layers className="w-3.5 h-3.5 text-slate-500" />
            View Discovered URLs Table
          </Link>
        </div>

        {/* Interactive Filter Bar */}
        <div className="bg-white p-4 rounded-xl border border-slate-200/90 shadow-sm space-y-3 text-xs">
          <div className="flex flex-wrap items-center gap-3">
            {/* Search */}
            <div className="relative flex-1 min-w-[200px]">
              <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
              <input
                type="text"
                placeholder="Search issues by keyword, title, or fix..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-9 pr-3 py-2 border border-slate-300 rounded-lg text-xs focus:outline-none focus:ring-1 focus:ring-brand-500"
              />
            </div>

            {/* Severity Filter */}
            <select
              value={selectedSeverity}
              onChange={(e) => setSelectedSeverity(e.target.value)}
              className="px-3 py-2 border border-slate-300 rounded-lg bg-slate-50 text-xs font-medium focus:outline-none"
            >
              <option value="">All Severities</option>
              <option value="critical">Critical</option>
              <option value="high">High</option>
              <option value="medium">Medium</option>
              <option value="low">Low</option>
              <option value="informational">Informational</option>
            </select>

            {/* Category Filter */}
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="px-3 py-2 border border-slate-300 rounded-lg bg-slate-50 text-xs font-medium focus:outline-none"
            >
              <option value="">All Categories</option>
              <option value="crawlability">Crawlability</option>
              <option value="on_page">On-Page SEO</option>
              <option value="internal_linking">Internal Linking</option>
              <option value="structured_data">Structured Data</option>
              <option value="performance">Performance</option>
              <option value="duplicates">Duplicates</option>
            </select>

            {/* Status Filter */}
            <select
              value={selectedStatus}
              onChange={(e) => setSelectedStatus(e.target.value)}
              className="px-3 py-2 border border-slate-300 rounded-lg bg-slate-50 text-xs font-medium focus:outline-none"
            >
              <option value="">All Statuses</option>
              <option value="open">Open</option>
              <option value="in_progress">In Progress</option>
              <option value="resolved">Resolved</option>
              <option value="ignored">Ignored</option>
            </select>

            {(selectedSeverity || selectedCategory || selectedStatus || searchQuery) && (
              <button
                onClick={() => {
                  setSelectedSeverity('');
                  setSelectedCategory('');
                  setSelectedStatus('');
                  setSearchQuery('');
                }}
                className="px-2.5 py-1.5 text-slate-500 hover:text-slate-800 font-medium"
              >
                Clear Filters
              </button>
            )}
          </div>
        </div>

        {/* Prioritized Issues Table */}
        <div className="bg-white rounded-xl border border-slate-200/90 shadow-sm overflow-hidden">
          {issues.length === 0 ? (
            <div className="py-16 text-center text-slate-500 text-xs">
              <CheckCircle2 className="w-10 h-10 text-emerald-500 mx-auto mb-2" />
              <p className="font-semibold text-slate-800 text-sm">No issues match the selected criteria.</p>
              <p className="mt-1">All checks evaluated cleanly or filter parameters excluded active findings.</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-50 text-slate-500 font-semibold border-b border-slate-200 uppercase tracking-wider">
                  <tr>
                    <th className="py-3 px-4 w-12 text-center">Rank</th>
                    <th className="py-3 px-4 w-24">Priority</th>
                    <th className="py-3 px-4 w-28">Severity</th>
                    <th className="py-3 px-6">Issue & Suggested Correction</th>
                    <th className="py-3 px-4 w-24">Affected</th>
                    <th className="py-3 px-4 w-20">Effort</th>
                    <th className="py-3 px-4 w-28">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-200">
                  {issues.map((iss, index) => {
                    const effortLabel =
                      iss.estimated_effort < 0.25 ? 'Low' : iss.estimated_effort < 0.55 ? 'Medium' : 'High';

                    return (
                      <tr
                        key={iss.id}
                        onClick={() => setActiveIssue(iss)}
                        className="hover:bg-slate-50 cursor-pointer transition-colors"
                      >
                        <td className="py-3 px-4 text-center font-mono font-bold text-slate-400">
                          #{index + 1}
                        </td>

                        <td className="py-3 px-4">
                          <div className="inline-flex items-baseline font-mono font-bold text-slate-900 bg-slate-100 px-2 py-0.5 rounded">
                            <span>{Math.round(iss.priority_score)}</span>
                            <span className="text-[10px] text-slate-400 ml-0.5">/100</span>
                          </div>
                        </td>

                        <td className="py-3 px-4">
                          <SeverityBadge severity={iss.severity} size="sm" />
                        </td>

                        <td className="py-3 px-6">
                          <div className="font-semibold text-slate-900 leading-snug">{iss.title}</div>
                          <div className="text-[11px] text-slate-500 line-clamp-1 mt-0.5">
                            {iss.suggested_fix}
                          </div>
                        </td>

                        <td className="py-3 px-4 font-mono text-slate-600">
                          {iss.affected_page_count} page{iss.affected_page_count > 1 ? 's' : ''}
                        </td>

                        <td className="py-3 px-4">
                          <span
                            className={`text-[11px] font-medium ${
                              effortLabel === 'Low'
                                ? 'text-emerald-700'
                                : effortLabel === 'Medium'
                                ? 'text-amber-700'
                                : 'text-slate-600'
                            }`}
                          >
                            {effortLabel}
                          </span>
                        </td>

                        <td className="py-3 px-4" onClick={(e) => e.stopPropagation()}>
                          <StatusBadge status={iss.status} />
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>

      {/* Slide-over Issue Details Drawer */}
      <IssueDrawer
        issue={activeIssue}
        onClose={() => setActiveIssue(null)}
        onStatusChange={handleStatusChange}
      />
    </div>
  );
};
