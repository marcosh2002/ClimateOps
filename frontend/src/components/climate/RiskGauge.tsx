'use client';

import { motion, useMotionValue, useSpring, useTransform } from 'framer-motion';
import { useState } from 'react';
import { cn } from '@/lib/utils';
import type { RiskType, ClimateRiskDetail } from '@/types';

interface RiskGaugeProps {
  risks: ClimateRiskDetail;
  size?: number;
  interactive?: boolean;
  showLabels?: boolean;
  className?: string;
}

const RISK_CONFIG: Record<RiskType, { label: string; icon: string; color: string }> = {
  heat: { label: 'Heat', icon: '☀️', color: 'var(--risk-high)' },
  flood: { label: 'Flood', icon: '🌊', color: 'var(--risk-medium)' },
  water_stress: { label: 'Water Stress', icon: '💧', color: 'var(--risk-low)' },
  drought: { label: 'Drought', icon: '🏜️', color: 'var(--risk-high)' },
};

const RISK_ORDER: RiskType[] = ['heat', 'flood', 'water_stress', 'drought'];

export function RiskGauge({
  risks,
  size = 320,
  interactive = true,
  showLabels = true,
  className,
}: RiskGaugeProps) {
  const [hoveredRisk, setHoveredRisk] = useState<RiskType | null>(null);
  const [focusedRisk, setFocusedRisk] = useState<RiskType | null>(null);

  const radius = size / 2 - 20;
  const center = size / 2;
  const strokeWidth = 28;
  const circumference = 2 * Math.PI * radius;

  const segments = RISK_ORDER.map((riskType, index) => {
    const risk = risks[riskType];
    const score = risk.score;
    const percentage = score / 100;
    const startAngle = (index / 4) * 360 - 90;
    const endAngle = startAngle + percentage * 360;

    const isActive = interactive && (hoveredRisk === riskType || focusedRisk === riskType);

    const path = (
      <motion.path
        key={riskType}
        d={`M ${center} ${center - radius} A ${radius} ${radius} 0 ${percentage > 0.5 ? 1 : 0} 1 ${center + radius * Math.cos((endAngle * Math.PI) / 180)} ${center + radius * Math.sin((endAngle * Math.PI) / 180)}`}
        fill="none"
        stroke={RISK_CONFIG[riskType].color}
        strokeWidth={strokeWidth}
        strokeLinecap="round"
        strokeDasharray={circumference}
        strokeDashoffset={circumference}
        initial={{ strokeDashoffset: circumference }}
        animate={{ strokeDashoffset: circumference * (1 - percentage) }}
        transition={{ duration: 1.2, delay: index * 0.15, ease: [0.4, 0, 0.2, 1] }}
        style={{
          transformOrigin: `${center}px ${center}px`,
          transform: isActive ? 'scale(1.08)' : 'scale(1)',
          filter: isActive ? 'drop-shadow(0 0 8px currentColor)' : 'none',
        }}
        onMouseEnter={() => interactive && setHoveredRisk(riskType)}
        onMouseLeave={() => setHoveredRisk(null)}
        onFocus={() => interactive && setFocusedRisk(riskType)}
        onBlur={() => setFocusedRisk(null)}
        tabIndex={interactive ? 0 : -1}
        role="img"
        aria-label={`${RISK_CONFIG[riskType].label} risk: ${score}%, ${risk.severity}`}
      />
    );

    return path;
  });

  const overallRisk = Math.max(...RISK_ORDER.map((r) => risks[r].score));
  const overallLevel = getRiskLevel(overallRisk);
  const dominantRisk = RISK_ORDER.reduce((a, b) => (risks[a].score > risks[b].score ? a : b));

  return (
    <div className={cn('relative inline-flex flex-col items-center', className)}>
      <div className="relative" style={{ width: size, height: size }}>
        <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} role="img" aria-label={`Risk gauge showing ${dominantRisk} as dominant risk`}>
          <defs>
            <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
              <feGaussianBlur stdDeviation="4" result="coloredBlur" />
              <feMerge>
                <feMergeNode in="coloredBlur" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>
          </defs>
          {/* Background ring */}
          <circle
            cx={center}
            cy={center}
            r={radius}
            fill="none"
            stroke="var(--theme-border)"
            strokeWidth={strokeWidth}
            opacity={0.3}
          />
          {segments}
          {/* Center content */}
          <motion.div
            className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none"
            style={{ transformOrigin: 'center' }}
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ duration: 0.8, delay: 0.6, ease: [0.4, 0, 0.2, 1] }}
          >
            <span className="text-display font-display text-theme-text-primary font-bold">
              {overallRisk}%
            </span>
            <span className={cn('badge mt-2', `badge-risk-${overallLevel.toLowerCase()}`)}>
              {overallLevel}
            </span>
            {showLabels && (
              <span className="mt-2 text-sm text-theme-text-muted font-medium">
                {RISK_CONFIG[dominantRisk].icon} {RISK_CONFIG[dominantRisk].label} dominant
              </span>
            )}
          </motion.div>
        </svg>
      </div>

      {showLabels && (
        <div className="grid grid-cols-2 gap-3 mt-6 w-full max-w-xs">
          {RISK_ORDER.map((riskType) => {
            const risk = risks[riskType];
            const isHovered = hoveredRisk === riskType;

            return (
              <motion.button
                key={riskType}
                className={cn(
                  'p-3 rounded-organic-sm border border-theme-border bg-theme-bg-secondary',
                  'transition-all duration-fast text-left',
                  'hover:border-theme-accent hover:bg-theme-accent/5',
                  isHovered && 'border-theme-accent bg-theme-accent/10 shadow-organic-hover'
                )}
                onMouseEnter={() => interactive && setHoveredRisk(riskType)}
                onMouseLeave={() => setHoveredRisk(null)}
                onFocus={() => interactive && setFocusedRisk(riskType)}
                onBlur={() => setFocusedRisk(null)}
                tabIndex={interactive ? 0 : -1}
                whileHover={{ y: -2 }}
                whileTap={{ scale: 0.98 }}
              >
                <div className="flex items-center gap-2">
                  <span className="text-lg" aria-hidden="true">{RISK_CONFIG[riskType].icon}</span>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium text-theme-text-primary truncate">
                        {RISK_CONFIG[riskType].label}
                      </span>
                      <span className={cn('font-mono font-bold', `text-risk-${risk.severity.toLowerCase()}`)}>
                        {risk.score}%
                      </span>
                    </div>
                    <div className="h-1.5 bg-theme-bg-accent rounded-full overflow-hidden mt-1">
                      <motion.div
                        className="h-full rounded-full"
                        style={{ backgroundColor: RISK_CONFIG[riskType].color }}
                        initial={{ width: 0 }}
                        animate={{ width: `${risk.score}%` }}
                        transition={{ duration: 1, delay: 0.4, ease: [0.4, 0, 0.2, 1] }}
                      />
                    </div>
                  </div>
                </div>
              </motion.button>
            );
          })}
        </div>
      )}
    </div>
  );
}

function getRiskLevel(score: number): 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL' {
  if (score <= 30) return 'LOW';
  if (score <= 60) return 'MEDIUM';
  if (score <= 80) return 'HIGH';
  return 'CRITICAL';
}