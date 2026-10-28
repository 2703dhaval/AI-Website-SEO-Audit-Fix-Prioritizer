import React from 'react';

interface ScoreBadgeProps {
  score: number;
  size?: 'sm' | 'md' | 'lg';
  showLabel?: boolean;
}

export const ScoreBadge: React.FC<ScoreBadgeProps> = ({ score, size = 'md', showLabel = true }) => {
  const rounded = Math.round(score * 10) / 10;

  let colorClass = 'text-emerald-600 bg-emerald-50 border-emerald-200';
  let grade = 'Excellent';

  if (rounded < 60) {
    colorClass = 'text-rose-600 bg-rose-50 border-rose-200';
    grade = 'Poor';
  } else if (rounded < 80) {
    colorClass = 'text-amber-600 bg-amber-50 border-amber-200';
    grade = 'Fair';
  }

  const dimensions = {
    sm: 'text-sm px-2 py-0.5 border',
    md: 'text-lg px-3 py-1 border',
    lg: 'text-3xl px-5 py-2.5 border-2 font-bold',
  }[size];

  return (
    <div className="inline-flex items-center gap-2">
      <div className={`inline-flex items-baseline font-mono font-bold rounded-lg ${dimensions} ${colorClass}`}>
        <span>{rounded.toFixed(1)}</span>
        <span className="text-xs font-normal opacity-70 ml-1">/100</span>
      </div>
      {showLabel && size !== 'sm' && (
        <span className="text-xs font-medium text-slate-500 uppercase tracking-wide">
          {grade}
        </span>
      )}
    </div>
  );
};
