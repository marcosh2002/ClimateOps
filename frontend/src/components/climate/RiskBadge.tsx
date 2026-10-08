'use client';

import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';
import type { RiskLevel } from '@/types';

interface RiskBadgeProps {
  score: number;
  label: string;
  size?: 'sm' | 'md' | 'lg';
  animate?: boolean;
  showTrend?: 'up' | 'down' | 'stable';
  trendValue?: number;
  className?: string;
}

const sizeConfig = {
  sm: { ringSize: 40, strokeWidth: 4, fontSize: 'text-xs', gap: 'gap-1' },
  md: { ringSize: 56, strokeWidth: 5, fontSize: 'text-sm', gap: 'gap-2' },
  lg: { ringSize: 80, strokeWidth: 6, fontSize: 'text-base', gap: 'gap-3' },
};

const circumference = (size: number) => 2 * Math.PI * (size / 2 - sizeConfig.sm.strokeWidth);

export function RiskBadge({
  score,
  label,
  size = 'md',
  animate = false,
  showTrend,
  trendValue,
  className,
}: RiskBadgeProps) {
  const level = getRiskLevel(score);
  const config = sizeConfig[size];
  const radius = config.ringSize / 2 - config.strokeWidth;
  const circumferenceValue = 2 * Math.PI * radius;
  const offset = circumferenceValue - (score / 100) * circumferenceValue;

  const trendIcons = {
    up: '↗',
    down: '↘',
    stable: '→',
  };

  const trendColors = {
    up: 'text-risk-high',
    down: 'text-risk-low',
    stable: 'text-theme-text-muted',
  };

  return (
    <div className={cn('inline-flex flex-col items-center', className)}>
      <div className="relative">
        <svg
          className={cn('transform -rotate-90', animate && level === 'CRITICAL' && 'animate-pulse-critical')}
          width={config.ringSize}
          height={config.ringSize}
          viewBox={`0 0 ${config.ringSize} ${config.ringSize}`}
          role="img"
          aria-label={`${label}: ${score}%, ${level}`}
        >
          <circle
            className="text-theme-border"
            cx={config.ringSize / 2}
            cy={config.ringSize / 2}
            r={radius}
            fill="none"
            strokeWidth={config.strokeWidth}
          />
          <motion.circle
            className={cn(
              'transition-all duration-1000 ease-out',
              `text-risk-${level.toLowerCase()}`
            )}
            cx={config.ringSize / 2}
            cy={config.ringSize / 2}
            r={radius}
            fill="none"
            strokeWidth={config.strokeWidth}
            strokeLinecap="round"
            strokeDasharray={circumferenceValue}
            strokeDashoffset={animate ? offset : circumferenceValue}
            initial={{ strokeDashoffset: circumferenceValue }}
            animate={{ strokeDashoffset: offset }}
            transition={{ duration: 1, ease: [0.4, 0, 0.2, 1] }}
          />
        </svg>
        <div className="absolute inset-0 flex items-center justify-center">
          <span className={cn(config.fontSize, 'font-bold text-theme-text-primary')}>
            {score}%
          </span>
        </div>
      </div>
      <div className={cn('flex flex-col items-center mt-1', config.gap)}>
        <span className={cn('text-xs font-medium uppercase tracking-wide', `badge-risk-${level.toLowerCase()}`)}>
          {level}
        </span>
        <span className="text-xs text-theme-text-muted">{label}</span>
        {showTrend && (
          <span
            className={cn('flex items-center gap-0.5 text-xs font-medium', trendColors[showTrend])}
            aria-label={`${trendValue ? `${trendValue > 0 ? '+' : ''}${trendValue}%` : ''} ${showTrend}`}
          >
            {trendIcons[showTrend]}
            {trendValue !== undefined && (
              <span>{trendValue > 0 ? '+' : ''}{trendValue}%</span>
            )}
          </span>
        )}
      </div>
    </div>
  );
}

function getRiskLevel(score: number): RiskLevel {
  if (score <= 30) return 'LOW';
  if (score <= 60) return 'MEDIUM';
  if (score <= 80) return 'HIGH';
  return 'CRITICAL';
}