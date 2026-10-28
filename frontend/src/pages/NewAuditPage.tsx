import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ShieldCheck, Info, ArrowRight, AlertTriangle } from 'lucide-react';
import { api } from '../services/api';

export const NewAuditPage: React.FC = () => {
  const [url, setUrl] = useState('');
  const [auditName, setAuditName] = useState('');
  const [maxPages, setMaxPages] = useState(25);
  const [maxDepth, setMaxDepth] = useState(3);
  const [crawlDelay, setCrawlDelay] = useState(0.5);
  const [excludePaths, setExcludePaths] = useState('/admin, /cart, /checkout');
  const [authorizedConsent, setAuthorizedConsent] = useState(false);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!url.trim()) {
      setError('Website URL is required.');
      return;
    }

    if (!authorizedConsent) {
      setError('Please acknowledge crawl authorization and robots.txt compliance.');
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const patterns = excludePaths
        .split(',')
        .map((p) => p.trim())
        .filter((p) => p.length > 0);

      const audit = await api.createAudit({
        url: url.trim(),
        audit_name: auditName.trim() || undefined,
        max_pages: maxPages,
        max_depth: maxDepth,
        crawl_delay_seconds: crawlDelay,
        exclude_patterns: patterns,
      });

      navigate(`/audits/${audit.id}/progress`);
    } catch (err: any) {
      setError(err.message || 'Failed to initiate audit');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 py-10">
      <div className="bg-white rounded-2xl border border-slate-200/90 shadow-sm p-6 sm:p-8">
        <div className="border-b border-slate-200 pb-5 mb-6">
          <h1 className="text-xl sm:text-2xl font-bold text-slate-900 tracking-tight">Configure New Technical SEO Audit</h1>
          <p className="text-xs text-slate-500 mt-1">
            Specify crawl boundaries, rate limits, and URL scoping. Our crawler enforces strict SSRF protections and robots.txt policies.
          </p>
        </div>

        {error && (
          <div className="mb-6 p-4 rounded-xl bg-rose-50 border border-rose-200 flex items-start gap-3 text-rose-800 text-xs font-medium">
            <AlertTriangle className="w-4 h-4 text-rose-600 flex-shrink-0 mt-0.5" />
            <div>
              <span className="font-semibold block">Audit Validation Error:</span>
              <span>{error}</span>
            </div>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6 text-xs sm:text-sm">
          {/* Target URL */}
          <div>
            <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
              Target Website URL <span className="text-rose-500">*</span>
            </label>
            <input
              type="url"
              required
              placeholder="https://example.com"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              className="w-full px-3.5 py-2.5 border border-slate-300 rounded-lg text-slate-900 placeholder:text-slate-400 font-mono text-sm focus:outline-none focus:ring-2 focus:ring-brand-600"
            />
            <p className="mt-1 text-[11px] text-slate-500">
              Only HTTP and HTTPS URLs are permitted. Internal IP addresses, localhost, and cloud metadata destinations are strictly rejected.
            </p>
          </div>

          {/* Audit Label Name */}
          <div>
            <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
              Audit Name / Label (Optional)
            </label>
            <input
              type="text"
              placeholder="e.g., Scalezix Production Technical Audit"
              value={auditName}
              onChange={(e) => setAuditName(e.target.value)}
              className="w-full px-3.5 py-2.5 border border-slate-300 rounded-lg text-slate-900 placeholder:text-slate-400 text-sm focus:outline-none focus:ring-2 focus:ring-brand-600"
            />
          </div>

          {/* Scoping Parameters Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-2">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Max Crawl Pages
              </label>
              <select
                value={maxPages}
                onChange={(e) => setMaxPages(parseInt(e.target.value, 10))}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg bg-slate-50 text-xs font-medium focus:outline-none"
              >
                <option value={10}>10 Pages (Quick Test)</option>
                <option value={25}>25 Pages (Safe Default)</option>
                <option value={50}>50 Pages (Deep Audit)</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Max Crawl Depth
              </label>
              <select
                value={maxDepth}
                onChange={(e) => setMaxDepth(parseInt(e.target.value, 10))}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg bg-slate-50 text-xs font-medium focus:outline-none"
              >
                <option value={1}>1 Hop (Root level only)</option>
                <option value={2}>2 Hops</option>
                <option value={3}>3 Hops (Recommended)</option>
                <option value={4}>4 Hops</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Crawl Delay (Seconds)
              </label>
              <select
                value={crawlDelay}
                onChange={(e) => setCrawlDelay(parseFloat(e.target.value))}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg bg-slate-50 text-xs font-medium focus:outline-none"
              >
                <option value={0.2}>0.2s (Fast)</option>
                <option value={0.5}>0.5s (Safe Default)</option>
                <option value={1.0}>1.0s (Polite)</option>
                <option value={2.0}>2.0s (Strict Rate Limit)</option>
              </select>
            </div>
          </div>

          {/* Path Exclusions */}
          <div>
            <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
              Path Exclusions (Comma-separated substrings)
            </label>
            <input
              type="text"
              placeholder="/admin, /cart, /checkout, /private"
              value={excludePaths}
              onChange={(e) => setExcludePaths(e.target.value)}
              className="w-full px-3.5 py-2.5 border border-slate-300 rounded-lg text-slate-900 font-mono text-xs focus:outline-none focus:ring-2 focus:ring-brand-600"
            />
          </div>

          {/* Compliance & Authorization Checkbox */}
          <div className="p-4 rounded-xl bg-slate-50 border border-slate-200">
            <label className="flex items-start gap-3 cursor-pointer">
              <input
                type="checkbox"
                required
                checked={authorizedConsent}
                onChange={(e) => setAuthorizedConsent(e.target.checked)}
                className="mt-0.5 rounded border-slate-300 text-brand-900 focus:ring-brand-600 w-4 h-4"
              />
              <span className="text-xs text-slate-600 leading-relaxed">
                I verify that I have permission to crawl this target domain. I understand the crawler will respect the target's declared <b>robots.txt</b> rules, apply rate limits, and reject private network destinations.
              </span>
            </label>
          </div>

          {/* Submit Action */}
          <div className="flex justify-end pt-3">
            <button
              type="submit"
              disabled={loading}
              className="inline-flex items-center gap-2 px-6 py-2.5 bg-brand-900 hover:bg-brand-800 text-white font-semibold rounded-xl text-xs sm:text-sm shadow-md transition-colors disabled:opacity-50"
            >
              {loading ? (
                'Initializing Audit...'
              ) : (
                <>
                  <span>Launch Technical Audit</span>
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
