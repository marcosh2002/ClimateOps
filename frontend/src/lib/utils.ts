import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';
import type { ClimateRiskDetail, RiskAssessment, RiskLevel, RiskType } from '@/types';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatRiskScore(score: number): string {
  return `${Math.round(score)}%`;
}

export function getRiskLevel(score: number): 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL' {
  if (score <= 30) return 'LOW';
  if (score <= 60) return 'MEDIUM';
  if (score <= 80) return 'HIGH';
  return 'CRITICAL';
}

export function getRiskColorClass(level: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL'): string {
  switch (level) {
    case 'LOW': return 'badge-risk-low';
    case 'MEDIUM': return 'badge-risk-medium';
    case 'HIGH': return 'badge-risk-high';
    case 'CRITICAL': return 'badge-risk-critical';
  }
}

export function getRiskIcon(level: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL'): string {
  switch (level) {
    case 'LOW': return '🟢';
    case 'MEDIUM': return '🟡';
    case 'HIGH': return '🟠';
    case 'CRITICAL': return '🔴';
  }
}

export function formatTimestamp(isoString: string): string {
  const date = new Date(isoString);
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

export function formatDateTime(isoString: string): string {
  const date = new Date(isoString);
  return date.toLocaleString([], {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

export function timeAgo(isoString: string): string {
  const now = new Date();
  const then = new Date(isoString);
  const diffMs = now.getTime() - then.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);

  if (diffMins < 1) return 'just now';
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  return `${diffDays}d ago`;
}

export function getDominantRisk(risk: RiskAssessment): RiskType {
  const risks = {
    heat: risk.heatRisk,
    flood: risk.floodRisk,
    water_stress: risk.waterStressRisk,
    drought: risk.droughtRisk,
  };
  return Object.entries(risks).reduce((a, b) => (a[1] > b[1] ? a : b))[0] as RiskType;
}

export function getThemeClass(riskType: RiskType | null, isCritical = false): string {
  if (!riskType) return '';
  const base = `theme-${riskType.replace('_', '-')}`;
  return isCritical ? `${base} theme-critical` : base;
}

export function haversineDistance(
  lat1: number,
  lon1: number,
  lat2: number,
  lon2: number
): number {
  const R = 6371;
  const dLat = ((lat2 - lat1) * Math.PI) / 180;
  const dLon = ((lon2 - lon1) * Math.PI) / 180;
  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos((lat1 * Math.PI) / 180) *
      Math.cos((lat2 * Math.PI) / 180) *
      Math.sin(dLon / 2) *
      Math.sin(dLon / 2);
  return 2 * R * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
}

export function debounce<T extends (...args: any[]) => any>(
  fn: T,
  ms: number
): (...args: Parameters<T>) => void {
  let timeoutId: ReturnType<typeof setTimeout>;
  return (...args: Parameters<T>) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => fn(...args), ms);
  };
}

export function throttle<T extends (...args: any[]) => any>(
  fn: T,
  ms: number
): (...args: Parameters<T>) => void {
  let lastCall = 0;
  return (...args: Parameters<T>) => {
    const now = Date.now();
    if (now - lastCall >= ms) {
      lastCall = now;
      fn(...args);
    }
  };
}