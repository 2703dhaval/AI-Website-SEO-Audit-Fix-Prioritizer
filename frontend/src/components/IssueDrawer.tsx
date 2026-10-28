import React, { useState } from 'react';
import { X, Check, Copy, ExternalLink, Lightbulb, AlertCircle, Wrench, ShieldAlert } from 'lucide-react';
import { SEOIssue } from '../types/api';
import { SeverityBadge } from './SeverityBadge';
import { StatusBadge } from './StatusBadge';

interface IssueDrawerProps {
  issue: SEOIssue | null;
  onClose: () => void;
  onStatusChange: (issueId: string, newStatus: string) => Promise<void>;
}

export const IssueDrawer: React.FC<IssueDrawerProps> = ({ issue, onClose, onStatusChange }) => {
  const [updating, setUpdating] = useState(false);
  const [copied, setCopied] = useState(false);

  if (!issue) return null;

  const handleStatusSelect = async (newStatus: string) => {
    try {
      setUpdating(true);
      await onStatusChange(issue.id, newStatus);
    } finally {
      setUpdating(false);
    }
  };

  const handleCopyCode = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="fixed inset-0 z-50 overflow-hidden bg-slate-900/40 backdrop-blur-sm flex justify-end">
      <div className="w-full max-w-2xl bg-white h-full shadow-2xl flex flex-col transform transition-transform duration-300">
        {/* Header */}
        <div className="px-6 py-5 border-b border-slate-200 flex items-start justify-between bg-slate-50/50">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <SeverityBadge severity={issue.severity} />
              <span className="text-xs font-mono uppercase bg-slate-200/70 text-slate-700 px-2 py-0.5 rounded">
                {issue.issue_code}
              </span>
              <span className="text-xs text-slate-500 capitalize">• {issue.category.replace('_', ' ')}</span>
            </div>
            <h2 className="text-lg font-bold text-slate-900 leading-snug">{issue.title}</h2>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Scrollable Content Body */}
        <div className="flex-1 overflow-y-auto px-6 py-5 space-y-6">
          {/* Status and Priority Score Bar */}
          <div className="grid grid-cols-2 gap-4 p-4 rounded-xl bg-slate-50 border border-slate-200/80">
            <div>
              <span className="text-xs font-medium text-slate-500 uppercase tracking-wider block mb-1.5">
                Issue Status
              </span>
              <div className="flex items-center gap-2">
                <StatusBadge status={issue.status} />
                <select
                  disabled={updating}
                  value={issue.status}
                  onChange={(e) => handleStatusSelect(e.target.value)}
                  className="text-xs border border-slate-300 rounded-md px-2 py-1 bg-white focus:outline-none focus:ring-1 focus:ring-brand-500"
                >
                  <option value="open">Open</option>
                  <option value="in_progress">In Progress</option>
                  <option value="resolved">Resolved</option>
                  <option value="ignored">Ignored</option>
                </select>
              </div>
            </div>

            <div>
              <span className="text-xs font-medium text-slate-500 uppercase tracking-wider block mb-1.5">
                Fix Priority Score
              </span>
              <div className="flex items-baseline gap-1.5">
                <span className="text-2xl font-bold font-mono text-slate-900">
                  {Math.round(issue.priority_score)}
                </span>
                <span className="text-xs text-slate-500 font-medium">/100</span>
                <span className="text-xs text-brand-700 font-medium ml-1">
                  (Impact: {Math.round(issue.impact * 100)}%, Effort:{' '}
                  {issue.estimated_effort < 0.25 ? 'Low' : issue.estimated_effort < 0.55 ? 'Med' : 'High'})
                </span>
              </div>
            </div>
          </div>

          {/* Description */}
          <div>
            <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2 flex items-center gap-1.5">
              <AlertCircle className="w-4 h-4 text-slate-400" />
              Issue Summary
            </h3>
            <p className="text-sm text-slate-700 leading-relaxed bg-white border border-slate-200/80 p-3.5 rounded-lg">
              {issue.description}
            </p>
          </div>

          {/* Why It Matters for SEO */}
          {issue.why_it_matters && (
            <div>
              <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                <Lightbulb className="w-4 h-4 text-amber-500" />
                Why This Matters for SEO
              </h3>
              <p className="text-sm text-slate-700 leading-relaxed bg-amber-50/40 border border-amber-200/60 p-3.5 rounded-lg">
                {issue.why_it_matters}
              </p>
            </div>
          )}

          {/* Suggested Fix & Example Code */}
          <div>
            <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2 flex items-center gap-1.5">
              <Wrench className="w-4 h-4 text-brand-600" />
              Recommended Correction
            </h3>
            <div className="space-y-2">
              <p className="text-sm text-slate-800 font-medium bg-slate-50 border border-slate-200 p-3.5 rounded-lg">
                {issue.suggested_fix}
              </p>
              {issue.example_fix && (
                <div className="relative rounded-lg bg-slate-900 text-slate-100 p-3.5 text-xs font-mono overflow-x-auto">
                  <div className="flex justify-between items-center mb-2 pb-1 border-b border-slate-800 text-slate-400">
                    <span>Suggested Code / Markup</span>
                    <button
                      onClick={() => handleCopyCode(issue.example_fix!)}
                      className="flex items-center gap-1 text-[11px] text-slate-400 hover:text-white"
                    >
                      {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                      {copied ? 'Copied' : 'Copy'}
                    </button>
                  </div>
                  <pre className="whitespace-pre-wrap">{issue.example_fix}</pre>
                </div>
              )}
            </div>
          </div>

          {/* Stored Evidence List */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider flex items-center gap-1.5">
                <ShieldAlert className="w-4 h-4 text-slate-400" />
                Stored Audit Evidence ({issue.evidences?.length || issue.affected_page_count} Affected URLs)
              </h3>
            </div>
            <div className="space-y-3">
              {(issue.evidences || []).map((ev, i) => (
                <div key={i} className="border border-slate-200 rounded-lg p-3 bg-white text-xs space-y-2">
                  <div className="flex items-center justify-between font-mono text-slate-700 bg-slate-50 px-2 py-1 rounded break-all">
                    <span>{ev.page_url}</span>
                    <a
                      href={ev.page_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-brand-600 hover:text-brand-800 ml-2"
                    >
                      <ExternalLink className="w-3.5 h-3.5 inline" />
                    </a>
                  </div>
                  {ev.observed_value && (
                    <div>
                      <span className="font-semibold text-rose-700">Observed: </span>
                      <span className="text-slate-700">{ev.observed_value}</span>
                    </div>
                  )}
                  {ev.expected_value && (
                    <div>
                      <span className="font-semibold text-emerald-700">Expected: </span>
                      <span className="text-slate-700">{ev.expected_value}</span>
                    </div>
                  )}
                  {ev.evidence_snippet && (
                    <div className="bg-slate-100 p-2 rounded font-mono text-[11px] text-slate-800 overflow-x-auto">
                      <code>{ev.evidence_snippet}</code>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="px-6 py-4 border-t border-slate-200 bg-slate-50 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 text-xs font-medium text-slate-700 hover:bg-slate-200 rounded-lg transition-colors"
          >
            Close Details
          </button>
        </div>
      </div>
    </div>
  );
};
