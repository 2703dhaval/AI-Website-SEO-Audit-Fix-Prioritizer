import React from 'react';
import { AlertTriangle, AlertCircle, Info, ShieldAlert } from 'lucide-react';

interface SeverityBadgeProps {
  severity: string;
  size?: 'sm' | 'md';
}

export const SeverityBadge: React.FC<SeverityBadgeProps> = ({ severity, size = 'md' }) => {
  const sev = severity.toLowerCase();

  let bg = 'bg-slate-100 text-slate-700 border-slate-200';
  let Icon = Info;

  if (sev === 'critical') {
    bg = 'bg-rose-50 text-rose-700 border-rose-200';
    Icon = ShieldAlert;
  } else if (sev === 'high') {
    bg = 'bg-orange-50 text-orange-700 border-orange-200';
    Icon = AlertTriangle;
  } else if (sev === 'medium') {
    bg = 'bg-amber-50 text-amber-700 border-amber-200';
    Icon = AlertCircle;
  } else if (sev === 'low') {
    bg = 'bg-blue-50 text-blue-700 border-blue-200';
    Icon = Info;
  }

  const padding = size === 'sm' ? 'px-2 py-0.5 text-xs' : 'px-2.5 py-1 text-xs';

  return (
    <span className={`inline-flex items-center gap-1.5 font-medium rounded-md border ${bg} ${padding}`}>
      <Icon className={size === 'sm' ? 'w-3 h-3' : 'w-3.5 h-3.5'} />
      <span className="capitalize">{severity}</span>
    </span>
  );
};
