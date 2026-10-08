'use client';

import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';
import { Card } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { MapPin, Clock, TrendingUp, AlertTriangle } from 'lucide-react';
import type { Incident, IncidentSeverity } from '@/types';

interface IncidentCardProps {
  incident: Incident;
  locationName?: string;
  onClick: () => void;
  isSelected?: boolean;
  className?: string;
}

const SEVERITY_CONFIG: Record<IncidentSeverity, { icon: string; label: string }> = {
  WARNING: { icon: '⚠️', label: 'Warning' },
  CRITICAL: { icon: '🔴', label: 'Critical' },
  EXTREME: { icon: '💀', label: 'Extreme' },
};

const RISK_LEVEL_MAP = {
  WARNING: 'MEDIUM' as const,
  CRITICAL: 'CRITICAL' as const,
  EXTREME: 'CRITICAL' as const,
};

const TYPE_ICONS: Record<string, string> = {
  HEAT: '🌡️',
  FLOOD: '🌊',
  HEAVY_RAIN: '🌧️',
  WATER_STRESS: '💧',
  DROUGHT: '☀️',
};

export function IncidentCard({
  incident,
  locationName,
  onClick,
  isSelected = false,
  className,
}: IncidentCardProps) {
  const severityConfig = SEVERITY_CONFIG[incident.severity];
  const typeIcon = TYPE_ICONS[incident.type] || '⚠️';
  const isDemo = incident.source?.startsWith('DEMO SCENARIO') ?? false;

  return (
    <motion.article
      className={cn(
        'card-organic cursor-pointer transition-all duration-normal',
        'hover:shadow-organic-hover hover:-translate-y-1',
        'focus-visible:ring-2 focus-visible:ring-theme-accent focus-visible:ring-offset-2',
        isSelected && 'ring-2 ring-theme-accent shadow-organic-hover',
        className
      )}
      onClick={onClick}
      onKeyDown={(e) => (e.key === 'Enter' || e.key === ' ') && onClick()}
      tabIndex={0}
      role="button"
      aria-label={`View ${incident.type} incident in ${locationName || incident.locationId}`}
      aria-pressed={isSelected}
      whileHover={{ y: -2 }}
      whileTap={{ scale: 0.98 }}
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
    >
      <div className="p-4">
        <div className="flex items-start justify-between gap-3">
          <div className="flex items-center gap-3 flex-1 min-w-0">
            <div className={cn(
              'w-12 h-12 rounded-organic-sm flex items-center justify-center text-2xl flex-shrink-0',
              `badge badge-risk-${incident.severity.toLowerCase()}`
            )}>
              <span aria-hidden="true">{typeIcon}</span>
            </div>
            <div className="min-w-0">
              <div className="flex items-center gap-2 flex-wrap">
                <h3 className="font-heading text-h3 text-theme-text-primary truncate">
                  {incident.type}
                </h3>
                <Badge variant="risk" riskLevel={RISK_LEVEL_MAP[incident.severity]}>
                  {severityConfig.icon} {severityConfig.label}
                </Badge>
                {isDemo && <Badge variant="info" size="sm">DEMO</Badge>}
              </div>
              <p className="text-body-sm text-theme-text-muted truncate mt-1">
                {locationName || incident.locationId}
              </p>
            </div>
          </div>
          <div className="flex flex-col items-end gap-1 flex-shrink-0">
            <div className="text-right">
              <p className="font-mono font-bold text-lg text-theme-text-primary">
                {incident.riskScore}%
              </p>
              <p className="text-xs text-theme-text-muted">Risk Score</p>
            </div>
          </div>
        </div>

        <div className="mt-4 pt-4 border-t border-theme-divider flex flex-wrap items-center justify-between gap-3 text-sm">
          <div className="flex items-center gap-2 text-theme-text-muted">
            <MapPin className="w-4 h-4" aria-hidden="true" />
            <span>{incident.locationId}</span>
          </div>
          <div className="flex items-center gap-2 text-theme-text-muted">
            <Clock className="w-4 h-4" aria-hidden="true" />
            <span>Updated {formatTimeAgo(incident.lastUpdated)}</span>
          </div>
          <div className="flex items-center gap-2 text-theme-text-muted">
            <TrendingUp className="w-4 h-4" aria-hidden="true" />
            <span>Next check in {incident.nextCheck ? formatTimeUntil(incident.nextCheck) : '—'}</span>
          </div>
        </div>

        {incident.status === 'CRITICAL' || incident.status === 'EXTREME' ? (
          <motion.div
            className="mt-3 p-3 rounded-organic-sm bg-risk-critical/10 border border-risk-critical/20 flex items-center gap-2"
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            role="alert"
          >
            <AlertTriangle className="w-5 h-5 text-risk-critical flex-shrink-0" aria-hidden="true" />
            <span className="text-sm font-medium text-risk-critical">
              Critical severity — Immediate attention required
            </span>
          </motion.div>
        ) : null}
      </div>
    </motion.article>
  );
}

function formatTimeAgo(isoString: string): string {
  const now = new Date();
  const then = new Date(isoString);
  const diffMs = now.getTime() - then.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);

  if (diffMins < 1) return 'just now';
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  return `${Math.floor(diffHours / 24)}d ago`;
}

function formatTimeUntil(isoString: string): string {
  const now = new Date();
  const then = new Date(isoString);
  const diffMs = then.getTime() - now.getTime();
  const diffMins = Math.floor(diffMs / 60000);

  if (diffMins < 1) return 'now';
  if (diffMins < 60) return `${diffMins}m`;
  return `${Math.floor(diffMins / 60)}h ${diffMins % 60}m`;
}