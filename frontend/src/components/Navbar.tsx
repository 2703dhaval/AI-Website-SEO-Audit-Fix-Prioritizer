import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Search, Plus, Sparkles, ShieldCheck } from 'lucide-react';
import { api } from '../services/api';

export const Navbar: React.FC = () => {
  const navigate = useNavigate();

  const handleOpenSample = async () => {
    try {
      const sample = await api.getSampleReport();
      navigate(`/audits/${sample.id}`);
    } catch (e) {
      console.error('Failed to load sample report', e);
    }
  };

  return (
    <header className="sticky top-0 z-40 bg-white/95 backdrop-blur border-b border-slate-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo & Product Brand */}
          <div className="flex items-center gap-3">
            <Link to="/" className="flex items-center gap-2.5">
              <div className="w-9 h-9 rounded-lg bg-brand-900 text-white flex items-center justify-center font-bold text-lg shadow-sm">
                <Search className="w-5 h-5 text-brand-300" />
              </div>
              <div>
                <span className="font-bold text-lg tracking-tight text-slate-900 block leading-tight">
                  SEO Audit Pro
                </span>
                <span className="text-[10px] text-slate-500 font-medium tracking-wide uppercase block">
                  AI Fix Prioritizer
                </span>
              </div>
            </Link>

            {/* Scalezix Badge */}
            <div className="hidden md:flex items-center ml-4 pl-4 border-l border-slate-200">
              <span className="text-xs bg-slate-100 text-slate-600 px-2.5 py-1 rounded-full font-medium flex items-center gap-1.5">
                <ShieldCheck className="w-3.5 h-3.5 text-brand-600" />
                Scalezix Enterprise Assessment
              </span>
            </div>
          </div>

          {/* Navigation Links & Actions */}
          <div className="flex items-center gap-3">
            <Link
              to="/dashboard"
              className="text-sm font-medium text-slate-600 hover:text-slate-900 px-3 py-1.5 rounded-lg hover:bg-slate-50 transition-colors"
            >
              Dashboard
            </Link>
            <Link
              to="/reports"
              className="text-sm font-medium text-slate-600 hover:text-slate-900 px-3 py-1.5 rounded-lg hover:bg-slate-50 transition-colors"
            >
              Reports
            </Link>
            <Link
              to="/settings"
              className="text-sm font-medium text-slate-600 hover:text-slate-900 px-3 py-1.5 rounded-lg hover:bg-slate-50 transition-colors"
            >
              Docs & Limits
            </Link>

            <button
              onClick={handleOpenSample}
              className="hidden sm:inline-flex items-center gap-1.5 text-xs font-semibold text-brand-800 bg-brand-50 hover:bg-brand-100 border border-brand-200 px-3 py-2 rounded-lg transition-colors"
              title="Open the real pre-crawled Scalezix technical SEO report"
            >
              <Sparkles className="w-3.5 h-3.5 text-brand-600" />
              Scalezix Sample Report
            </button>

            <Link
              to="/audits/new"
              className="inline-flex items-center gap-1.5 text-xs font-semibold text-white bg-brand-900 hover:bg-brand-800 px-3.5 py-2 rounded-lg shadow-sm transition-colors"
            >
              <Plus className="w-3.5 h-3.5" />
              New Audit
            </Link>
          </div>
        </div>
      </div>
    </header>
  );
};
