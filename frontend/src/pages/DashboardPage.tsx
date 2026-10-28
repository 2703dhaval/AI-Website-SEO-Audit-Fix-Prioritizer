import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  Globe,
  AlertTriangle,
  ShieldAlert,
  Activity,
  Plus,
  ArrowUpRight,
  Sparkles,
  BarChart3,
  Calendar
} from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from 'recharts';
import { api } from '../services/api';
import { DashboardStats } from '../types/api';
import { MetricCard } from '../components/MetricCard';
import { ScoreBadge } from '../components/ScoreBadge';
import { LoadingSkeleton } from '../components/LoadingSkeleton';

export const DashboardPage: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.getDashboardStats();
      setStats(data);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch dashboard metrics');
    } finally {
      setLoading(false);
    }
  };

  const handleOpenSample = async () => {
    try {
      const sample = await api.getSampleReport();
      navigate(`/audits/${sample.id}`);
    } catch {
      setError('Could not open sample report');
    }
  };

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
        <div className="h-8 w-48 bg-slate-200 rounded animate-pulse" />
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="h-28 bg-slate-200 rounded-xl animate-pulse" />
          ))}
        </div>
        <LoadingSkeleton rows={6} />
      </div>
    );
  }

  if (error || !stats) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 text-center">
        <AlertTriangle className="w-12 h-12 text-amber-500 mx-auto mb-3" />
        <h2 className="text-lg font-bold text-slate-900">Failed to load dashboard</h2>
        <p className="text-sm text-slate-500 mt-1">{error}</p>
        <button
          onClick={loadDashboard}
          className="mt-4 px-4 py-2 bg-brand-900 text-white rounded-lg text-xs font-semibold"
        >
          Retry
        </button>
      </div>
    );
  }

  // Prepare chart data
  const severityColors: Record<string, string> = {
    critical: '#dc2626',
    high: '#ea580c',
    medium: '#d97706',
    low: '#2563eb',
    informational: '#64748b',
  };

  const severityData = Object.entries(stats.severity_distribution || {}).map(([key, val]) => ({
    name: key.charAt(0).toUpperCase() + key.slice(1),
    value: val,
    color: severityColors[key] || '#94a3b8',
  }));

  const categoryData = Object.entries(stats.category_distribution || {}).map(([key, val]) => ({
    name: key.replace('_', ' ').replace(/\b\w/g, (l) => l.toUpperCase()),
    count: val,
  }));

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Page Title & Quick Actions */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-200 pb-5">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Technical SEO Dashboard</h1>
          <p className="text-xs text-slate-500 mt-1">
            Aggregated diagnostics, domain health benchmarks, and real-time audit records.
          </p>
        </div>

        <div className="flex items-center gap-2.5">
          <button
            onClick={handleOpenSample}
            className="inline-flex items-center gap-1.5 px-3 py-2 bg-white hover:bg-slate-50 border border-slate-200 text-slate-700 rounded-lg text-xs font-semibold shadow-sm transition-colors"
          >
            <Sparkles className="w-3.5 h-3.5 text-brand-600" />
            Scalezix Sample Report
          </button>
          <Link
            to="/audits/new"
            className="inline-flex items-center gap-1.5 px-3.5 py-2 bg-brand-900 hover:bg-brand-800 text-white rounded-lg text-xs font-semibold shadow-sm transition-colors"
          >
            <Plus className="w-3.5 h-3.5" />
            Start New Audit
          </Link>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Websites Audited"
          value={stats.websites_audited}
          subtitle={`${stats.total_audits} total audit runs completed`}
          icon={Globe}
        />
        <MetricCard
          title="Average Health Score"
          value={`${stats.avg_health_score}/100`}
          subtitle="Across all audited domains"
          icon={Activity}
          badge={{
            text: stats.avg_health_score >= 80 ? 'Good' : stats.avg_health_score >= 60 ? 'Moderate' : 'Action Required',
            variant: stats.avg_health_score >= 80 ? 'success' : stats.avg_health_score >= 60 ? 'warning' : 'danger',
          }}
        />
        <MetricCard
          title="Critical & High Deficiencies"
          value={stats.critical_and_high_issues}
          subtitle={`${stats.critical_issues} critical, ${stats.high_issues} high severity`}
          icon={ShieldAlert}
          badge={{ text: 'Priority Fixes', variant: stats.critical_and_high_issues > 0 ? 'danger' : 'success' }}
        />
        <MetricCard
          title="Total Issues Identified"
          value={stats.total_issues}
          subtitle="Traceable findings in database"
          icon={BarChart3}
        />
      </div>

      {/* Visual Charts: Severity Breakdown & Category Distribution */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Severity Chart */}
        <div className="bg-white p-5 rounded-xl border border-slate-200/80 shadow-sm flex flex-col justify-between">
          <div>
            <h3 className="text-sm font-bold text-slate-900">Issue Severity Breakdown</h3>
            <p className="text-xs text-slate-500 mt-0.5">Distribution across all active audits</p>
          </div>

          <div className="h-52 mt-4">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={severityData}
                  cx="50%"
                  cy="50%"
                  innerRadius={45}
                  outerRadius={75}
                  paddingAngle={3}
                  dataKey="value"
                >
                  {severityData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip
                  formatter={(val: any) => [`${val} issues`, 'Count']}
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b', borderRadius: '8px', color: '#fff', fontSize: '12px' }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>

          <div className="flex flex-wrap items-center justify-center gap-3 pt-3 border-t border-slate-100 text-[11px]">
            {severityData.map((d, i) => (
              <div key={i} className="flex items-center gap-1.5 font-medium text-slate-600">
                <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: d.color }} />
                <span>{d.name}: {d.value}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Category Chart */}
        <div className="lg:col-span-2 bg-white p-5 rounded-xl border border-slate-200/80 shadow-sm">
          <div>
            <h3 className="text-sm font-bold text-slate-900">Defects by Audit Category</h3>
            <p className="text-xs text-slate-500 mt-0.5">Identified technical SEO flaws grouped by discipline</p>
          </div>

          <div className="h-64 mt-4">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={categoryData} margin={{ top: 10, right: 10, left: -20, bottom: 25 }}>
                <XAxis dataKey="name" angle={-15} textAnchor="end" tick={{ fontSize: 11, fill: '#64748b' }} interval={0} />
                <YAxis tick={{ fontSize: 11, fill: '#64748b' }} allowDecimals={false} />
                <Tooltip
                  formatter={(val: any) => [`${val} issues`, 'Total Detected']}
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b', borderRadius: '8px', color: '#fff', fontSize: '12px' }}
                />
                <Bar dataKey="count" fill="#205384" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Recent Audits Table */}
      <div className="bg-white rounded-xl border border-slate-200/80 shadow-sm overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-200 flex items-center justify-between bg-slate-50/50">
          <div>
            <h3 className="text-sm font-bold text-slate-900">Recent Website Audits</h3>
            <p className="text-xs text-slate-500 mt-0.5">Audits stored in local database</p>
          </div>
          <Link
            to="/reports"
            className="text-xs font-semibold text-brand-700 hover:text-brand-900 inline-flex items-center gap-1"
          >
            All Reports & Comparison <ArrowUpRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 text-slate-500 font-semibold border-b border-slate-200 uppercase tracking-wider">
              <tr>
                <th className="py-3 px-6">Domain / Target</th>
                <th className="py-3 px-6">Status</th>
                <th className="py-3 px-6">Health Score</th>
                <th className="py-3 px-6">Crawled Pages</th>
                <th className="py-3 px-6">Audit Date</th>
                <th className="py-3 px-6 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200">
              {stats.recent_audits.map((audit) => (
                <tr key={audit.id} className="hover:bg-slate-50/80 transition-colors">
                  <td className="py-3.5 px-6 font-medium text-slate-900">
                    <div className="font-semibold text-slate-900">{audit.normalized_domain}</div>
                    <div className="text-[11px] text-slate-400 font-mono truncate max-w-xs">{audit.submitted_url}</div>
                  </td>
                  <td className="py-3.5 px-6">
                    <span
                      className={`inline-flex items-center px-2 py-0.5 rounded text-[11px] font-medium capitalize ${
                        audit.status === 'completed'
                          ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                          : audit.status === 'running'
                          ? 'bg-blue-50 text-blue-700 border border-blue-200 animate-pulse'
                          : 'bg-slate-100 text-slate-600'
                      }`}
                    >
                      {audit.status}
                    </span>
                  </td>
                  <td className="py-3.5 px-6">
                    <ScoreBadge score={audit.seo_health_score} size="sm" showLabel={false} />
                  </td>
                  <td className="py-3.5 px-6 text-slate-600 font-mono">
                    {audit.total_crawled_pages} / {audit.total_discovered_pages}
                  </td>
                  <td className="py-3.5 px-6 text-slate-500">
                    <span className="flex items-center gap-1.5">
                      <Calendar className="w-3.5 h-3.5 text-slate-400" />
                      {new Date(audit.created_at).toLocaleDateString()}
                    </span>
                  </td>
                  <td className="py-3.5 px-6 text-right">
                    <Link
                      to={`/audits/${audit.id}`}
                      className="inline-flex items-center gap-1 text-xs font-semibold text-brand-700 hover:text-brand-900 bg-brand-50 hover:bg-brand-100 px-2.5 py-1.5 rounded transition-colors"
                    >
                      View Results
                      <ArrowUpRight className="w-3.5 h-3.5" />
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
