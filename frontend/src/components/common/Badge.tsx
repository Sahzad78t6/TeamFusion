import React from 'react';
import { clsx } from 'clsx';

interface BadgeProps {
  children: React.ReactNode;
  variant?: 'purple' | 'blue' | 'cyan' | 'green' | 'amber' | 'rose' | 'outline' | 'glass';
  size?: 'sm' | 'md';
  icon?: React.ReactNode;
  className?: string;
}

export const Badge: React.FC<BadgeProps> = ({
  children,
  variant = 'purple',
  size = 'md',
  icon,
  className,
}) => {
  const sizes = {
    sm: 'px-2 py-0.5 text-[10px] font-semibold gap-1',
    md: 'px-2.5 py-1 text-xs font-semibold gap-1.5',
  };

  const variants = {
    purple: 'bg-purple-500/10 text-purple-300 border border-purple-500/20',
    blue: 'bg-blue-500/10 text-blue-300 border border-blue-500/20',
    cyan: 'bg-cyan-500/10 text-cyan-300 border border-cyan-500/20',
    green: 'bg-emerald-500/10 text-emerald-300 border border-emerald-500/20',
    amber: 'bg-amber-500/10 text-amber-300 border border-amber-500/20',
    rose: 'bg-rose-500/10 text-rose-300 border border-rose-500/20',
    outline: 'bg-transparent text-slate-300 border border-slate-700',
    glass: 'bg-white/5 text-slate-200 border border-white/10 backdrop-blur-md',
  };

  return (
    <span
      className={clsx(
        'inline-flex items-center rounded-full transition-all',
        sizes[size],
        variants[variant],
        className
      )}
    >
      {icon && <span className="shrink-0">{icon}</span>}
      {children}
    </span>
  );
};
