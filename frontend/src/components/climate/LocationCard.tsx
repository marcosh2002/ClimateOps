'use client';

import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';
import { RiskBadge } from './RiskBadge';
import { Card } from '@/components/ui/Card';
import type { Location, ClimateRiskDetail } from '@/types';

interface LocationCardProps {
  location: Location;
  risk?: ClimateRiskDetail;
  incident?: boolean;
  variant?: 'search' | 'monitored' | 'incident' | 'simulation';
  onSelect: () => void;
  className?: string;
}

const LANDSCAPE_ILLUSTRATIONS: Record<string, string> = {
  default: '🌿',
  coastal: '🌊',
  desert: '🏜️',
  mountain: '⛰️',
  urban: '🏙️',
  river: '🌊',
  forest: '🌲',
};

function getLandscapeType(location: Location): string {
  const riskTypes = location.riskTypes || [];
  if (riskTypes.includes('FLOOD') || riskTypes.includes('HEAVY_RAIN')) return 'coastal';
  if (riskTypes.includes('HEAT') || riskTypes.includes('DROUGHT')) return 'desert';
  if (riskTypes.includes('WATER_STRESS')) return 'river';
  return 'default';
}

export function LocationCard({
  location,
  risk,
  incident = false,
  variant = 'search',
  onSelect,
  className,
}: LocationCardProps) {
  const landscape = getLandscapeType(location);
  const landscapeIcon = LANDSCAPE_ILLUSTRATIONS[landscape];
  const dominantRisk = risk
    ? Object.entries(risk).reduce((a, b) => (a[1].score > b[1].score ? a : b))[0]
    : null;
  const dominantScore = risk ? Math.max(...Object.values(risk).map((r) => r.score)) : 0;

  return (
    <motion.article
      className={cn(
        'card-organic group cursor-pointer overflow-hidden',
        'hover:shadow-organic-hover hover:-translate-y-1',
        'focus-visible:ring-2 focus-visible:ring-theme-accent focus-visible:ring-offset-2',
        className
      )}
      onClick={onSelect}
      onKeyDown={(e) => (e.key === 'Enter' || e.key === ' ') && onSelect()}
      tabIndex={0}
      role="button"
      aria-label={`View ${location.city || location.district || location.state}, ${location.country}`}
      whileHover={{ y: -4 }}
      whileTap={{ scale: 0.98 }}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
    >
      {/* Micro-landscape illustration */}
      <div className="relative h-32 w-full overflow-hidden bg-gradient-to-br from-theme-bg-accent to-theme-border">
        <div className="absolute inset-0 flex items-center justify-center text-6xl opacity-60 group-hover:opacity-100 group-hover:scale-110 transition-all duration-700">
          <span aria-hidden="true">{landscapeIcon}</span>
        </div>
        {dominantRisk && risk && (
          <div className="absolute top-3 right-3">
            <RiskBadge
              score={risk[dominantRisk as keyof ClimateRiskDetail]?.score || 0}
              label={dominantRisk}
              size="sm"
              animate
            />
          </div>
        )}
        {incident && (
          <div className="absolute top-3 left-3 animate-pulse">
            <span className="badge badge-risk-critical">🔴 LIVE</span>
          </div>
        )}
      </div>

      <div className="p-4">
        <div className="flex items-start justify-between gap-3">
          <div className="min-w-0">
            <h3 className="font-heading text-h3 text-theme-text-primary truncate">
              {location.city || location.district || location.state}
            </h3>
            <p className="text-body-sm text-theme-text-muted truncate">
              {location.state}, {location.country}
            </p>
          </div>
          {location.monitoringEnabled && (
            <span className="flex-shrink-0 badge bg-forest-100 text-forest-700 dark:bg-forest-900 dark:text-forest-300">
              📡 Monitored
            </span>
          )}
        </div>

        {risk && (
          <div className="mt-4 grid grid-cols-2 gap-2">
            {(['heat', 'flood', 'water_stress', 'drought'] as const).map((riskType) => {
              const r = risk[riskType];
              return (
                <div
                  key={riskType}
                  className="flex items-center gap-2 p-2 rounded-organic-sm bg-theme-bg-primary border border-theme-border"
                >
                  <span className="text-lg" aria-hidden="true">
                    {RISK_ICONS[riskType]}
                  </span>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-medium text-theme-text-secondary truncate">
                        {RISK_LABELS[riskType]}
                      </span>
                      <span className={cn('font-mono font-bold', `text-risk-${r.severity.toLowerCase()}`)}>
                        {r.score}%
                      </span>
                    </div>
                    <div className="h-1 bg-theme-border rounded-full overflow-hidden mt-1">
                      <motion.div
                        className="h-full rounded-full"
                        style={{ backgroundColor: `var(--risk-${r.severity.toLowerCase()})` }}
                        initial={{ width: 0 }}
                        animate={{ width: `${r.score}%` }}
                        transition={{ duration: 0.8, delay: 0.2, ease: [0.4, 0, 0.2, 1] }}
                      />
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </motion.article>
  );
}

const RISK_ICONS: Record<string, string> = {
  heat: '🌡️',
  flood: '🌊',
  water_stress: '💧',
  drought: '☀️',
};

const RISK_LABELS: Record<string, string> = {
  heat: 'Heat',
  flood: 'Flood',
  water_stress: 'Water Stress',
  drought: 'Drought',
};