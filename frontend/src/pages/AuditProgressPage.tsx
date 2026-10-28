import React, { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { Loader2, CheckCircle2, XCircle, AlertCircle, StopCircle, ArrowRight, Globe, Layers } from 'lucide-react';
import { api } from '../services/api';
import { ProgressResponse, Audit } from '../types/api';

export const AuditProgressPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [progress, setProgress] = useState<ProgressResponse | null>(null);
  const [audit, setAudit] = useState<Audit | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [cancelling, setCancelling] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    if (!id) return;

    let isMounted = true;
    let pollInterval: any = null;

    const fetchStatus = async () => {
      try {
        const [prog, aud] = await Promise.all([
          api.getAuditProgress(id),
          api.getAudit(id)
        ]);

        if (!isMounted) return;
        setProgress(prog);
        setAudit(aud);

        if (prog.status === 'completed') {
          clearInterval(pollInterval);
        } else if (prog.status === 'failed' || prog.status === 'cancelled') {
          clearInterval(pollInterval);
        }
      } catch (err: any) {
        if (!isMounted) return;
        setError(err.message || 'Failed to poll audit progress');
      }
    };

    fetchStatus();
    pollInterval = setInterval(fetchStatus, 1000); // 1-second live polling

    return () => {
      isMounted = false;
      clearInterval(pollInterval);
    };
  }, [id]);

  const handleCancel = async () => {
    if (!id) return;
    try {
      setCancelling(true);
      await api.cancelAudit(id);
      const updatedProg = await api.getAuditProgress(id);
      setProgress(updatedProg);
    } catch (err: any) {
      setError(err.message || 'Failed to cancel audit');
    } finally {
      setCancelling(false);
    }
  };

  const percent = progress
    ? Math.min(100, Math.round((progress.pages_crawled / Math.max(progress.pages_discovered, 1)) * 100))
    : 10;

  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 py-12">
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 sm:p-10 text-center">
        {/* Status Graphic */}
        <div className="mb-6 flex justify-center">
          {progress?.status === 'completed' ? (
            <div className="w-16 h-16 rounded-2xl bg-emerald-100 text-emerald-700 flex items-center justify-center shadow-sm">
              <CheckCircle2 className="w-9 h-9" />
            </div>
          ) : progress?.status === 'failed' ? (
            <div className="w-16 h-16 rounded-2xl bg-rose-100 text-rose-700 flex items-center justify-center shadow-sm">
              <XCircle className="w-9 h-9" />
            </div>
          ) : progress?.status === 'cancelled' ? (
            <div className="w-16 h-16 rounded-2xl bg-slate-200 text-slate-700 flex items-center justify-center shadow-sm">
              <AlertCircle className="w-9 h-9" />
            </div>
          ) : (
            <div className="w-16 h-16 rounded-2xl bg-brand-50 text-brand-700 flex items-center justify-center shadow-sm">
              <Loader2 className="w-9 h-9 animate-spin" />
            </div>
          )}
        </div>

        {/* Title & Target */}
        <h1 className="text-2xl font-bold text-slate-900 tracking-tight">
          {progress?.status === 'completed'
            ? 'Audit Completed Successfully'
            : progress?.status === 'failed'
            ? 'Audit Execution Failed'
            : progress?.status === 'cancelled'
            ? 'Audit Cancelled by User'
            : 'Auditing Website in Progress'}
        </h1>

        <div className="mt-2 inline-flex items-center gap-1.5 text-xs font-mono text-slate-600 bg-slate-100 px-3 py-1 rounded-full">
          <Globe className="w-3.5 h-3.5 text-slate-400" />
          <span>{audit?.submitted_url || 'Target Website'}</span>
        </div>

        {/* Progress Bar */}
        <div className="mt-8 max-w-md mx-auto">
          <div className="flex justify-between text-xs font-medium text-slate-600 mb-2">
            <span>{progress?.current_stage || 'Initializing crawler...'}</span>
            <span className="font-mono">{percent}%</span>
          </div>

          <div className="w-full bg-slate-100 rounded-full h-3 overflow-hidden border border-slate-200">
            <div
              className={`h-full transition-all duration-500 rounded-full ${
                progress?.status === 'completed'
                  ? 'bg-emerald-600'
                  : progress?.status === 'failed' || progress?.status === 'cancelled'
                  ? 'bg-slate-400'
                  : 'bg-brand-700'
              }`}
              style={{ width: `${percent}%` }}
            />
          </div>
        </div>

        {/* Metrics Grid */}
        <div className="grid grid-cols-3 gap-3 max-w-md mx-auto mt-8 p-4 rounded-xl bg-slate-50 border border-slate-200/80 text-xs text-center">
          <div>
            <span className="text-slate-400 block uppercase tracking-wider text-[10px] font-semibold">
              Discovered
            </span>
            <span className="text-lg font-bold font-mono text-slate-900 mt-0.5 block">
              {progress?.pages_discovered ?? 0}
            </span>
          </div>
          <div className="border-x border-slate-200">
            <span className="text-slate-400 block uppercase tracking-wider text-[10px] font-semibold">
              Crawled
            </span>
            <span className="text-lg font-bold font-mono text-slate-900 mt-0.5 block">
              {progress?.pages_crawled ?? 0}
            </span>
          </div>
          <div>
            <span className="text-slate-400 block uppercase tracking-wider text-[10px] font-semibold">
              Remaining
            </span>
            <span className="text-lg font-bold font-mono text-slate-900 mt-0.5 block">
              {progress?.pages_remaining ?? 0}
            </span>
          </div>
        </div>

        {/* Diagnostic Event Stream */}
        {progress?.latest_event && (
          <div className="mt-4 text-xs text-slate-500 font-mono">
            <span>Recent event: </span>
            <span className="text-slate-700 font-semibold">{progress.latest_event}</span>
          </div>
        )}

        {/* Action Buttons */}
        <div className="mt-10 flex items-center justify-center gap-3">
          {progress?.status === 'completed' ? (
            <Link
              to={`/audits/${id}`}
              className="inline-flex items-center gap-2 px-6 py-3 bg-emerald-600 hover:bg-emerald-700 text-white font-semibold rounded-xl text-sm shadow-md transition-colors"
            >
              <span>Inspect Full Audit Results</span>
              <ArrowRight className="w-4 h-4" />
            </Link>
          ) : progress?.status === 'running' || progress?.status === 'queued' ? (
            <button
              onClick={handleCancel}
              disabled={cancelling}
              className="inline-flex items-center gap-2 px-5 py-2.5 bg-rose-50 hover:bg-rose-100 text-rose-700 border border-rose-200 font-medium rounded-xl text-xs transition-colors"
            >
              <StopCircle className="w-4 h-4 text-rose-600" />
              <span>{cancelling ? 'Stopping...' : 'Cancel Crawl'}</span>
            </button>
          ) : (
            <Link
              to="/audits/new"
              className="inline-flex items-center gap-2 px-5 py-2.5 bg-brand-900 hover:bg-brand-800 text-white font-medium rounded-xl text-xs transition-colors"
            >
              <span>Start New Audit</span>
            </Link>
          )}
        </div>
      </div>
    </div>
  );
};
