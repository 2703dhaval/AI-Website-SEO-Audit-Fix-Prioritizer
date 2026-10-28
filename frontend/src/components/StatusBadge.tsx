import React from 'react';
import { CheckCircle2, Clock, EyeOff, CircleDot } from 'lucide-react';

interface StatusBadgeProps {
  status: string;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status }) => {
  const st = status.toLowerCase();

  const configs: Record<string, { bg: string; icon: any; label: string }> = {
    open: { bg: 'bg-rose-50 text-rose-700 border-rose-200', icon: CircleDot, label: 'Open' },
    in_progress: { bg: 'bg-blue-50 text-blue-700 border-blue-200', icon: Clock, label: 'In Progress' },
    resolved: { bg: 'bg-emerald-50 text-emerald-700 border-emerald-200', icon: CheckCircle2, label: 'Resolved' },
    ignored: { bg: 'bg-slate-100 text-slate-600 border-slate-200', icon: EyeOff, label: 'Ignored' },
  };

  const current = configs[st] || configs.open;
  const Icon = current.icon;

  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium border ${current.bg}`}>
      <Icon className="w-3 h-3" />
      <span>{current.label}</span>
    </span>
  );
};
