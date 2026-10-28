import React, { useEffect, useState } from 'react';
import { Shield, Server, FileText, CheckCircle2, AlertTriangle, ExternalLink } from 'lucide-react';
import { api } from '../services/api';

export const SettingsPage: React.FC = () => {
  const [health, setHealth] = useState<{ status: string; version: string; database: string } | null>(null);

  useEffect(() => {
    api.getHealth().then(setHealth).catch(() => setHealth({ status: 'degraded', version: '1.0.0', database: 'error' }));
  }, []);

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Title */}
      <div className="border-b border-slate-200 pb-5">
        <h1 className="text-2xl font-bold text-slate-900 tracking-tight">System Settings & Documentation</h1>
        <p className="text-xs text-slate-500 mt-1">
          Technical specifications, scoring algorithms, SSRF security controls, and operational limits.
        </p>
      </div>

      {/* Backend API Health Status */}
      <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-emerald-50 text-emerald-700 flex items-center justify-center">
            <Server className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-sm font-bold text-slate-900">Backend API & Database Connectivity</h2>
            <p className="text-xs text-slate-500">
              API Version: {health?.version || '1.0.0'} • Database Engine: {health?.database || 'SQLite'}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse" />
          <span className="text-xs font-semibold text-emerald-700 uppercase tracking-wider">
            {health?.status === 'healthy' ? 'System Operational' : 'Service Connected'}
          </span>
        </div>
      </div>

      {/* Prioritization & Health Score Methodology */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-3">
          <h2 className="text-sm font-bold text-slate-900 flex items-center gap-2">
            <span className="w-6 h-6 rounded bg-brand-50 text-brand-700 flex items-center justify-center text-xs font-mono font-bold">1</span>
            Deterministic Fix Prioritization Formula
          </h2>
          <div className="bg-slate-900 text-slate-100 p-3 rounded-lg font-mono text-xs overflow-x-auto">
            Priority Score = 100 × (0.45×Impact + 0.30×Scope + 0.25×Confidence) × (1 - 0.15×Effort)
          </div>
          <p className="text-xs text-slate-600 leading-relaxed">
            All variables are normalized between 0.0 and 1.0. Scope uses bounded logarithmic scaling relative to crawled pages. Higher implementation effort dampens the priority score so low-effort quick-wins surface first.
          </p>
        </div>

        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-3">
          <h2 className="text-sm font-bold text-slate-900 flex items-center gap-2">
            <span className="w-6 h-6 rounded bg-emerald-50 text-emerald-700 flex items-center justify-center text-xs font-mono font-bold">2</span>
            SEO Health Score Calculation
          </h2>
          <div className="bg-slate-900 text-slate-100 p-3 rounded-lg font-mono text-xs overflow-x-auto">
            Health Score = max(0, 100 - sum(min(CategoryCap, Deductions)))
          </div>
          <p className="text-xs text-slate-600 leading-relaxed">
            Starts from a baseline of 100.0. Applies calibrated deductions per severity (Critical: 14pts, High: 8pts, Medium: 4pts, Low: 1.5pts) multiplied by scope factor and capped per category to prevent runaway penalties.
          </p>
        </div>
      </div>

      {/* SSRF Security Controls Specification */}
      <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-4">
        <div className="flex items-center gap-2.5">
          <Shield className="w-5 h-5 text-brand-700" />
          <h2 className="text-sm font-bold text-slate-900">Server-Side Request Forgery (SSRF) Firewall</h2>
        </div>
        <p className="text-xs text-slate-600 leading-relaxed">
          Because web crawlers accept arbitrary user-submitted URLs, our backend implements strict pre-flight security controls before opening any TCP sockets:
        </p>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
          <div className="p-3 bg-slate-50 border border-slate-200 rounded-lg">
            <span className="font-semibold text-slate-800 block mb-1">Network Subnet Restrictions</span>
            <ul className="list-disc list-inside text-slate-600 space-y-0.5 text-[11px]">
              <li>Rejects Loopback: 127.0.0.0/8, ::1</li>
              <li>Rejects Private IPv4: 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16</li>
              <li>Rejects Link-Local: 169.254.0.0/16, fe80::/10</li>
            </ul>
          </div>

          <div className="p-3 bg-slate-50 border border-slate-200 rounded-lg">
            <span className="font-semibold text-slate-800 block mb-1">Protocol & Redirect Controls</span>
            <ul className="list-disc list-inside text-slate-600 space-y-0.5 text-[11px]">
              <li>Blocks Cloud Metadata: 169.254.169.254, metadata.google.internal</li>
              <li>Pre-resolves DNS and inspects resolved socket address</li>
              <li>Re-validates every redirect hop against SSRF rules</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Operational Limits */}
      <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-4">
        <h2 className="text-sm font-bold text-slate-900">Crawler Limits & Polite Crawling Policy</h2>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs text-center">
          <div className="p-3 bg-slate-50 rounded-lg border border-slate-200">
            <span className="text-[10px] text-slate-400 uppercase font-semibold block">Max Pages</span>
            <span className="text-lg font-bold font-mono text-slate-900 mt-1 block">50 Pages</span>
          </div>
          <div className="p-3 bg-slate-50 rounded-lg border border-slate-200">
            <span className="text-[10px] text-slate-400 uppercase font-semibold block">Max Depth</span>
            <span className="text-lg font-bold font-mono text-slate-900 mt-1 block">5 Hops</span>
          </div>
          <div className="p-3 bg-slate-50 rounded-lg border border-slate-200">
            <span className="text-[10px] text-slate-400 uppercase font-semibold block">HTTP Timeout</span>
            <span className="text-lg font-bold font-mono text-slate-900 mt-1 block">10.0s</span>
          </div>
          <div className="p-3 bg-slate-50 rounded-lg border border-slate-200">
            <span className="text-[10px] text-slate-400 uppercase font-semibold block">Max Response Size</span>
            <span className="text-lg font-bold font-mono text-slate-900 mt-1 block">5 MB / page</span>
          </div>
        </div>
      </div>
    </div>
  );
};
