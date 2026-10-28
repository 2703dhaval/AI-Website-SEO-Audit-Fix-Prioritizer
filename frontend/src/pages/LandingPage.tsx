import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Search,
  ArrowRight,
  Shield,
  Zap,
  BarChart3,
  FileCheck2,
  Code2,
  Layers,
  Sparkles,
  ExternalLink,
  ChevronRight
} from 'lucide-react';
import { api } from '../services/api';

export const LandingPage: React.FC = () => {
  const [url, setUrl] = useState('');
  const [maxPages, setMaxPages] = useState('25');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  const handleStartAudit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!url.trim()) {
      setError('Please enter a website URL');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const audit = await api.createAudit({
        url: url.trim(),
        max_pages: parseInt(maxPages, 10),
        max_depth: 3,
        crawl_delay_seconds: 0.5
      });
      navigate(`/audits/${audit.id}/progress`);
    } catch (err: any) {
      setError(err.message || 'Failed to start audit');
    } finally {
      setLoading(false);
    }
  };

  const handleOpenScalezixSample = async () => {
    try {
      const sample = await api.getSampleReport();
      navigate(`/audits/${sample.id}`);
    } catch (err: any) {
      setError('Could not load sample report');
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col justify-between">
      {/* Hero Section */}
      <section className="relative overflow-hidden pt-12 pb-20 lg:pt-20 lg:pb-28">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 text-center">
          {/* Badge */}
          <div className="inline-flex items-center gap-2 bg-brand-50 border border-brand-200/80 px-3.5 py-1.5 rounded-full text-xs font-semibold text-brand-900 mb-6">
            <Sparkles className="w-4 h-4 text-brand-600" />
            <span>AI-Assisted SEO Audit & Deterministic Fix Prioritization</span>
          </div>

          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold text-slate-900 tracking-tight leading-tight">
            Find SEO Issues. <br className="hidden sm:inline" />
            <span className="text-brand-700">Prioritize Fixes.</span> Improve Your Website.
          </h1>

          <p className="mt-5 text-lg sm:text-xl text-slate-600 max-w-2xl mx-auto leading-relaxed">
            Crawls permitted websites, detects technical defects across on-page, crawlability, internal links, and structured data, and computes an evidence-based fix roadmap.
          </p>

          {/* Audit URL Launch Card */}
          <div className="mt-10 max-w-2xl mx-auto bg-white p-3 rounded-2xl shadow-xl border border-slate-200/90">
            <form onSubmit={handleStartAudit} className="flex flex-col sm:flex-row gap-2">
              <div className="relative flex-1">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                  <Search className="w-5 h-5" />
                </div>
                <input
                  type="url"
                  required
                  placeholder="https://example.com"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  className="block w-full pl-10 pr-3 py-3 border border-slate-300 rounded-xl text-sm placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-brand-600 focus:border-brand-600 font-mono"
                />
              </div>

              <div className="flex gap-2">
                <select
                  value={maxPages}
                  onChange={(e) => setMaxPages(e.target.value)}
                  className="px-3 py-3 border border-slate-300 rounded-xl text-xs font-medium text-slate-700 bg-slate-50 focus:outline-none"
                  title="Crawl Page Limit"
                >
                  <option value="10">10 Pages</option>
                  <option value="25">25 Pages (Safe Default)</option>
                  <option value="50">50 Pages</option>
                </select>

                <button
                  type="submit"
                  disabled={loading}
                  className="inline-flex items-center justify-center gap-2 px-6 py-3 bg-brand-900 hover:bg-brand-800 text-white text-sm font-semibold rounded-xl shadow-md transition-colors disabled:opacity-50"
                >
                  {loading ? (
                    'Validating...'
                  ) : (
                    <>
                      <span>Start Audit</span>
                      <ArrowRight className="w-4 h-4" />
                    </>
                  )}
                </button>
              </div>
            </form>

            {error && (
              <p className="mt-2 text-xs font-medium text-rose-600 text-left px-2">{error}</p>
            )}

            <div className="mt-3 pt-3 border-t border-slate-100 flex flex-wrap items-center justify-between text-xs text-slate-500 px-2">
              <span>Respects robots.txt and SSRF network controls.</span>
              <button
                type="button"
                onClick={handleOpenScalezixSample}
                className="text-brand-700 hover:text-brand-900 font-medium inline-flex items-center gap-1"
              >
                Inspect Scalezix Sample Report
                <ExternalLink className="w-3 h-3" />
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* Feature Pillars */}
      <section className="py-16 bg-white border-y border-slate-200">
        <div className="max-w-6xl mx-auto px-4 sm:px-6">
          <div className="text-center max-w-2xl mx-auto mb-12">
            <h2 className="text-2xl font-bold text-slate-900">Enterprise Technical SEO Architecture</h2>
            <p className="text-sm text-slate-600 mt-2">
              Engineered with safety, transparency, and deterministic mathematical prioritization at its core.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            <div className="p-6 rounded-xl border border-slate-200/80 bg-slate-50/50">
              <div className="w-10 h-10 rounded-lg bg-brand-100 text-brand-800 flex items-center justify-center mb-4">
                <Shield className="w-5 h-5" />
              </div>
              <h3 className="text-base font-bold text-slate-900">Strict SSRF Security Firewall</h3>
              <p className="mt-2 text-xs text-slate-600 leading-relaxed">
                Rejects loopback (127.0.0.1), private RFC 1918 subnets, cloud metadata (169.254.169.254), and pre-resolves DNS. Re-validates every redirect hop.
              </p>
            </div>

            <div className="p-6 rounded-xl border border-slate-200/80 bg-slate-50/50">
              <div className="w-10 h-10 rounded-lg bg-emerald-100 text-emerald-800 flex items-center justify-center mb-4">
                <Zap className="w-5 h-5" />
              </div>
              <h3 className="text-base font-bold text-slate-900">Deterministic Prioritization</h3>
              <p className="mt-2 text-xs text-slate-600 leading-relaxed">
                Fixes are ranked via formula: <i>100 × (0.45×Impact + 0.30×Scope + 0.25×Confidence) × (1 - 0.15×Effort)</i>. Transparent, reproducible, no arbitrary numbers.
              </p>
            </div>

            <div className="p-6 rounded-xl border border-slate-200/80 bg-slate-50/50">
              <div className="w-10 h-10 rounded-lg bg-amber-100 text-amber-800 flex items-center justify-center mb-4">
                <FileCheck2 className="w-5 h-5" />
              </div>
              <h3 className="text-base font-bold text-slate-900">Traceable Stored Evidence</h3>
              <p className="mt-2 text-xs text-slate-600 leading-relaxed">
                Every detected issue references exact observed vs. expected DOM conditions and HTML snippets, with downloadable PDF, CSV, and JSON exports.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* SEO Categories Grid */}
      <section className="py-16 bg-slate-50">
        <div className="max-w-6xl mx-auto px-4 sm:px-6">
          <div className="flex flex-col sm:flex-row sm:items-end justify-between mb-10">
            <div>
              <span className="text-xs font-bold text-brand-700 uppercase tracking-wider">Analysis Scope</span>
              <h2 className="text-2xl font-bold text-slate-900 mt-1">6 Comprehensive Audit Categories</h2>
            </div>
            <button
              onClick={() => navigate('/dashboard')}
              className="mt-3 sm:mt-0 text-xs font-semibold text-slate-700 hover:text-slate-900 inline-flex items-center gap-1"
            >
              View Audits Dashboard <ChevronRight className="w-4 h-4" />
            </button>
          </div>

          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {[
              { title: 'HTTP & Crawlability', desc: '4xx/5xx status codes, redirect chains/loops, robots.txt, mixed content, canonical tags.', icon: Layers },
              { title: 'On-Page Structure', desc: 'Title lengths, meta descriptions, H1 hierarchy, missing image alt attributes, viewport configuration.', icon: Code2 },
              { title: 'Internal Link Equity', desc: 'Broken links, links pointing to redirects, potential orphan pages, anchor text quality, crawl depth.', icon: ArrowRight },
              { title: 'Structured Data', desc: 'JSON-LD syntax validation, malformed objects, schema context (@context, @type) verification.', icon: Sparkles },
              { title: 'Performance Indicators', desc: 'Initial server response latency (TTFB), large HTML payloads, un-dimensioned layout shift images.', icon: BarChart3 },
              { title: 'Duplicates & Consistency', desc: 'Duplicate page titles, shared meta descriptions, text shingle Jaccard near-duplicate content detection.', icon: Shield }
            ].map((cat, idx) => (
              <div key={idx} className="bg-white p-5 rounded-xl border border-slate-200/80 shadow-sm">
                <cat.icon className="w-5 h-5 text-brand-700 mb-2" />
                <h3 className="text-sm font-bold text-slate-900">{cat.title}</h3>
                <p className="mt-1 text-xs text-slate-600 leading-relaxed">{cat.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-slate-900 text-slate-400 py-10 border-t border-slate-800 text-xs">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div>
            <span className="font-bold text-slate-200 text-sm">SEO Audit Pro</span>
            <span className="block text-[11px] text-slate-500 mt-0.5">
              Developed for Scalezix Internship Selection Assessment • Ahmedabad, India
            </span>
          </div>
          <div className="flex gap-6">
            <button onClick={() => navigate('/settings')} className="hover:text-slate-200">
              Documentation & Limits
            </button>
            <button onClick={handleOpenScalezixSample} className="hover:text-slate-200">
              Scalezix Sample Report
            </button>
            <button onClick={() => navigate('/dashboard')} className="hover:text-slate-200">
              Live Dashboard
            </button>
          </div>
        </div>
      </footer>
    </div>
  );
};
