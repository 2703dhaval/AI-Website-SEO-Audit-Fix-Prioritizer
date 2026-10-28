import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  FileText,
  Download,
  GitCompare,
  Trash2,
  Calendar,
  ArrowRight,
  TrendingUp,
  TrendingDown,
  Sparkles,
  AlertTriangle,
  Layers
} from 'lucide-react';
import { api } from '../services/api';
import { Audit } from '../types/api';
import { ScoreBadge } from '../components/ScoreBadge';
import { LoadingSkeleton } from '../components/LoadingSkeleton';

export const ReportsPage: React.FC = () => {
  const [audits, setAudits] = useState<Audit[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Comparison State
  const [compareAudit1, setCompareAudit1] = useState<string>('');
  const [compareAudit2, setCompareAudit2] = useState<string>('');
  const [comparisonResult, setComparisonResult] = useState<any>(null);
  const [comparing, setComparing] = useState(false);

  useEffect(() => {
    loadAudits();
  }, []);

  const loadAudits = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.listAudits(0, 100);
      setAudits(data);
      if (data.length >= 2) {
        setCompareAudit1(data[0].id);
        setCompareAudit2(data[1].id);
      } else if (data.length === 1) {
        setCompareAudit1(data[0].id);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to fetch audits');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteAudit = async (id: string, domain: string) => {
    if (window.confirm(`Permanently delete audit for ${domain}? This action cannot be reversed.`)) {
      try {
        await api.deleteAudit(id);
        setAudits((prev) => prev.filter((a) => a.id !== id));
        if (comparisonResult) setComparisonResult(null);
      } catch (err: any) {
        alert(err.message || 'Failed to delete audit');
      }
    }
  };

  const handleRunComparison = async () => {
    if (!compareAudit1 || !compareAudit2 || compareAudit1 === compareAudit2) {
      alert('Please select two distinct audits to compare.');
      return;
    }
    try {
      setComparing(true);
      const res = await api.compareAudits(compareAudit1, compareAudit2);
      setComparisonResult(res);
    } catch (err: any) {
      alert(err.message || 'Comparison failed');
    } finally {
      setComparing(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-10">
      {/* Title */}
      <div className="border-b border-slate-200 pb-5">
        <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Audit Reports & Historical Records</h1>
        <p className="text-xs text-slate-500 mt-1">
          Generate client-ready PDF deliverables, download Excel CSV fix lists, or perform audit regression comparisons.
        </p>
      </div>

      {/* Audit Comparison Tool */}
      <div className="bg-white rounded-2xl border border-slate-200/90 shadow-sm p-6 space-y-5">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-brand-50 text-brand-700 flex items-center justify-center">
            <GitCompare className="w-4 h-4" />
          </div>
          <div>
            <h2 className="text-base font-bold text-slate-900">Audit Comparison Engine</h2>
            <p className="text-xs text-slate-500">Measure SEO Health Score deltas and detect newly introduced or resolved defects</p>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-2">
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">Baseline Audit (Older)</label>
            <select
              value={compareAudit1}
              onChange={(e) => setCompareAudit1(e.target.value)}
              className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs bg-slate-50 focus:outline-none"
            >
              <option value="">Select Baseline Audit</option>
              {audits.map((a) => (
                <option key={a.id} value={a.id}>
                  {a.normalized_domain} — {new Date(a.created_at).toLocaleDateString()} ({a.seo_health_score} pts)
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">Comparison Audit (Newer)</label>
            <select
              value={compareAudit2}
              onChange={(e) => setCompareAudit2(e.target.value)}
              className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs bg-slate-50 focus:outline-none"
            >
              <option value="">Select Comparison Audit</option>
              {audits.map((a) => (
                <option key={a.id} value={a.id}>
                  {a.normalized_domain} — {new Date(a.created_at).toLocaleDateString()} ({a.seo_health_score} pts)
                </option>
              ))}
            </select>
          </div>

          <div className="flex items-end">
            <button
              onClick={handleRunComparison}
              disabled={comparing || !compareAudit1 || !compareAudit2}
              className="w-full px-4 py-2 bg-brand-900 hover:bg-brand-800 text-white rounded-lg text-xs font-semibold shadow-sm transition-colors disabled:opacity-50"
            >
              {comparing ? 'Analyzing Deltas...' : 'Compare Audits'}
            </button>
          </div>
        </div>

        {/* Comparison Result Display */}
        {comparisonResult && (
          <div className="mt-6 pt-5 border-t border-slate-200 space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-center">
              <div className="bg-slate-50 p-4 rounded-xl border border-slate-200">
                <span className="text-xs text-slate-500 uppercase tracking-wider block">Health Score Delta</span>
                <span
                  className={`text-2xl font-bold font-mono mt-1 block flex items-center justify-center gap-1 ${
                    comparisonResult.health_score_delta >= 0 ? 'text-emerald-600' : 'text-rose-600'
                  }`}
                >
                  {comparisonResult.health_score_delta >= 0 ? (
                    <TrendingUp className="w-5 h-5" />
                  ) : (
                    <TrendingDown className="w-5 h-5" />
                  )}
                  {comparisonResult.health_score_delta > 0 ? `+` : ''}
                  {comparisonResult.health_score_delta} pts
                </span>
              </div>

              <div className="bg-slate-50 p-4 rounded-xl border border-slate-200">
                <span className="text-xs text-slate-500 uppercase tracking-wider block">Issues Delta</span>
                <span className="text-2xl font-bold font-mono text-slate-800 mt-1 block">
                  {comparisonResult.total_issues_delta > 0 ? `+` : ''}
                  {comparisonResult.total_issues_delta} issues
                </span>
              </div>

              <div className="bg-slate-50 p-4 rounded-xl border border-slate-200">
                <span className="text-xs text-slate-500 uppercase tracking-wider block">Resolved Issues</span>
                <span className="text-2xl font-bold font-mono text-emerald-600 mt-1 block">
                  {comparisonResult.resolved_issues?.length || 0} fixed
                </span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Historical Audits Table */}
      <div className="bg-white rounded-2xl border border-slate-200/90 shadow-sm overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-200 bg-slate-50/50">
          <h2 className="text-sm font-bold text-slate-900">Historical Audit Records ({audits.length})</h2>
          <p className="text-xs text-slate-500 mt-0.5">Stored technical audits with downloadable outputs</p>
        </div>

        {loading ? (
          <div className="p-6">
            <LoadingSkeleton rows={5} />
          </div>
        ) : audits.length === 0 ? (
          <div className="py-16 text-center text-slate-500 text-xs">
            <p className="font-semibold text-slate-800 text-sm">No audits recorded yet.</p>
            <Link to="/audits/new" className="mt-3 inline-block text-brand-700 font-semibold hover:underline">
              Launch your first audit
            </Link>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 text-slate-500 font-semibold border-b border-slate-200 uppercase tracking-wider">
                <tr>
                  <th className="py-3 px-6">Domain / Target</th>
                  <th className="py-3 px-4">Score</th>
                  <th className="py-3 px-4">Crawled</th>
                  <th className="py-3 px-4">Date</th>
                  <th className="py-3 px-6 text-center">Export Downloads</th>
                  <th className="py-3 px-6 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200">
                {audits.map((a) => (
                  <tr key={a.id} className="hover:bg-slate-50 transition-colors">
                    <td className="py-3.5 px-6">
                      <div className="font-semibold text-slate-900">{a.normalized_domain}</div>
                      <div className="text-[11px] text-slate-400 font-mono truncate max-w-xs">{a.submitted_url}</div>
                    </td>

                    <td className="py-3.5 px-4">
                      <ScoreBadge score={a.seo_health_score} size="sm" showLabel={false} />
                    </td>

                    <td className="py-3.5 px-4 font-mono text-slate-600">
                      {a.total_crawled_pages} pages
                    </td>

                    <td className="py-3.5 px-4 text-slate-500">
                      <span className="flex items-center gap-1.5">
                        <Calendar className="w-3.5 h-3.5 text-slate-400" />
                        {new Date(a.created_at).toLocaleDateString()}
                      </span>
                    </td>

                    <td className="py-3.5 px-6 text-center">
                      <div className="inline-flex items-center gap-2">
                        <a
                          href={api.getReportPdfUrl(a.id)}
                          download
                          title="Download PDF Audit Report"
                          className="px-2 py-1 bg-slate-100 hover:bg-slate-200 text-slate-700 font-medium rounded text-[11px] inline-flex items-center gap-1"
                        >
                          <Download className="w-3 h-3 text-brand-700" /> PDF
                        </a>
                        <a
                          href={api.getExportCsvUrl(a.id)}
                          download
                          title="Download Excel CSV Fix List"
                          className="px-2 py-1 bg-slate-100 hover:bg-slate-200 text-slate-700 font-medium rounded text-[11px] inline-flex items-center gap-1"
                        >
                          <FileText className="w-3 h-3 text-emerald-700" /> CSV
                        </a>
                        <a
                          href={api.getExportJsonUrl(a.id)}
                          download
                          title="Download Raw JSON Schema Export"
                          className="px-2 py-1 bg-slate-100 hover:bg-slate-200 text-slate-700 font-medium rounded text-[11px] inline-flex items-center gap-1"
                        >
                          JSON
                        </a>
                      </div>
                    </td>

                    <td className="py-3.5 px-6 text-right">
                      <div className="inline-flex items-center gap-2">
                        <Link
                          to={`/audits/${a.id}`}
                          className="px-2.5 py-1 text-xs font-semibold text-brand-700 bg-brand-50 hover:bg-brand-100 rounded inline-flex items-center gap-1"
                        >
                          Inspect <ArrowRight className="w-3 h-3" />
                        </Link>
                        <button
                          onClick={() => handleDeleteAudit(a.id, a.normalized_domain)}
                          className="p-1 text-slate-400 hover:text-rose-600 rounded transition-colors"
                          title="Delete Audit"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
