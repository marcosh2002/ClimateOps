'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { cn } from '@/lib/utils';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Slider } from '@/components/ui/Slider';
import { Select } from '@/components/ui/Select';
import { RiskGauge } from '@/components/climate/RiskGauge';
import { AIInsight } from '@/components/climate/AIInsight';
import { X, ChevronDown, ChevronUp, Save, Share2, RotateCcw } from 'lucide-react';
import { useSimulationStore } from '@/store';
import type { SimulationParams, SimulationResponse, ClimateRiskDetail } from '@/types';

const SIMULATION_CONTROLS = [
  {
    key: 'temperature_change' as keyof SimulationParams,
    label: 'Temperature Change',
    unit: '°C',
    min: -10,
    max: 10,
    step: 0.5,
    marks: [
      { value: -10, label: '-10°C' },
      { value: 0, label: '0°C' },
      { value: 10, label: '+10°C' },
    ],
  },
  {
    key: 'humidity_change' as keyof SimulationParams,
    label: 'Humidity Change',
    unit: '%',
    min: -30,
    max: 20,
    step: 1,
    marks: [
      { value: -30, label: '-30%' },
      { value: 0, label: '0%' },
      { value: 20, label: '+20%' },
    ],
  },
  {
    key: 'rainfall_change_pct' as keyof SimulationParams,
    label: 'Rainfall Change',
    unit: '%',
    min: -80,
    max: 200,
    step: 5,
    marks: [
      { value: -80, label: '-80%' },
      { value: 0, label: '0%' },
      { value: 100, label: '+100%' },
      { value: 200, label: '+200%' },
    ],
  },
  {
    key: 'river_level_change' as keyof SimulationParams,
    label: 'River Level Change',
    unit: 'm',
    min: -5,
    max: 10,
    step: 0.5,
    marks: [
      { value: -5, label: '-5m' },
      { value: 0, label: '0m' },
      { value: 10, label: '+10m' },
    ],
  },
];

const RIVER_TREND_OPTIONS = [
  { value: 'RISING', label: 'Rising ↗' },
  { value: 'STABLE', label: 'Stable →' },
  { value: 'FALLING', label: 'Falling ↘' },
];

interface SimulationDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  locationId: string;
  originalRisks: ClimateRiskDetail;
  onRunSimulation: (params: SimulationParams) => Promise<void>;
}

export function SimulationDrawer({
  isOpen,
  onClose,
  locationId,
  originalRisks,
  onRunSimulation,
}: SimulationDrawerProps) {
  const {
    isActive,
    simulatedRisks,
    comparison,
    summary,
    aiExplanation,
    clearResults,
  } = useSimulationStore();

  const [params, setParams] = useState<SimulationParams>({});
  const [riverTrend, setRiverTrend] = useState<'RISING' | 'FALLING' | 'STABLE' | ''>('');
  const [isRunning, setIsRunning] = useState(false);

  useEffect(() => {
    if (!isOpen) {
      clearResults();
      setParams({});
      setRiverTrend('');
    }
  }, [isOpen, clearResults]);

  const handleParamChange = (key: keyof SimulationParams, value: number) => {
    setParams((prev) => ({ ...prev, [key]: value }));
  };

  const handleRunSimulation = async () => {
    setIsRunning(true);
    const simulationParams: SimulationParams = {
      ...params,
      river_trend: (riverTrend || undefined) as 'RISING' | 'FALLING' | 'STABLE' | undefined,
    };
    try {
      await onRunSimulation(simulationParams);
    } finally {
      setIsRunning(false);
    }
  };

  const handleReset = () => {
    clearResults();
    setParams({});
    setRiverTrend('');
  };

  const formatScenarioDescription = (): string => {
    const parts: string[] = [];
    if (params.temperature_change) parts.push(`Temperature ${params.temperature_change > 0 ? '+' : ''}${params.temperature_change}°C`);
    if (params.humidity_change) parts.push(`Humidity ${params.humidity_change > 0 ? '+' : ''}${params.humidity_change}%`);
    if (params.rainfall_change_pct) parts.push(`Rainfall ${params.rainfall_change_pct > 0 ? '+' : ''}${params.rainfall_change_pct}%`);
    if (params.river_level_change) parts.push(`River level ${params.river_level_change > 0 ? '+' : ''}${params.river_level_change}m`);
    if (riverTrend) parts.push(`River trend ${riverTrend}`);
    return parts.join('; ') || 'No changes';
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          <motion.div
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-40"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            aria-hidden="true"
          />
          <motion.aside
            className="fixed right-0 top-0 bottom-0 z-50 w-full max-w-2xl bg-theme-bg-primary border-l border-theme-border shadow-organic-hover flex flex-col"
            initial={{ x: '100%' }}
            animate={{ x: 0 }}
            exit={{ x: '100%' }}
            transition={{ type: 'spring', damping: 25, stiffness: 200 }}
            role="dialog"
            aria-modal="true"
            aria-labelledby="simulation-drawer-title"
          >
            {/* Header */}
            <div className="flex items-center justify-between p-4 border-b border-theme-divider">
              <motion.h2
                id="simulation-drawer-title"
                className="font-heading text-h2 text-theme-text-primary flex items-center gap-2"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
              >
                <span className="text-2xl" aria-hidden="true">🧪</span>
                What-If Simulation
              </motion.h2>
              <Button variant="ghost" size="sm" onClick={onClose} aria-label="Close simulation">
                <X className="w-5 h-5" />
              </Button>
            </div>

            {/* Content */}
            <div className="flex-1 overflow-y-auto p-4 space-y-6">
              {/* Current vs Simulated Gauges */}
              <motion.div className="grid grid-cols-2 gap-4" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
                <Card variant="outlined" padding="md">
                  <h3 className="font-medium text-theme-text-secondary mb-3 text-center">CURRENT</h3>
                  <RiskGauge risks={originalRisks} size={200} interactive={false} showLabels={false} />
                </Card>
                <Card variant="outlined" padding="md">
                  <h3 className="font-medium text-theme-text-secondary mb-3 text-center">SIMULATED</h3>
                  {simulatedRisks ? (
                    <RiskGauge risks={simulatedRisks} size={200} interactive={false} showLabels={false} />
                  ) : (
                    <div className="h-48 flex items-center justify-center text-theme-text-muted">
                      Adjust parameters to preview
                    </div>
                  )}
                </Card>
              </motion.div>

              {/* Comparison Table */}
              {comparison && (
                <motion.div className="card-organic overflow-hidden" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
                  <div className="p-4 border-b border-theme-divider">
                    <h3 className="font-heading text-h3 text-theme-text-primary">Risk Comparison</h3>
                    <p className="text-body-sm text-theme-text-muted mt-1">
                      {formatScenarioDescription()}
                    </p>
                  </div>
                  <div className="overflow-x-auto">
                    <table className="w-full" role="table">
                      <thead>
                        <tr className="border-b border-theme-divider">
                          <th className="text-left p-3 font-medium text-theme-text-secondary">Risk</th>
                          <th className="text-right p-3 font-medium text-theme-text-secondary">Current</th>
                          <th className="text-right p-3 font-medium text-theme-text-secondary">Simulated</th>
                          <th className="text-right p-3 font-medium text-theme-text-secondary">Change</th>
                          <th className="text-center p-3 font-medium text-theme-text-secondary">Severity</th>
                        </tr>
                      </thead>
                      <tbody>
                        {(['heat', 'flood', 'water_stress', 'drought'] as const).map((riskType) => {
                          const comp = comparison[riskType];
                          const orig = originalRisks[riskType];
                          const sim = simulatedRisks?.[riskType];
                          if (!comp || !sim) return null;

                          return (
                            <motion.tr
                              key={riskType}
                              className="border-b border-theme-divider/50"
                              initial={{ opacity: 0, x: -20 }}
                              animate={{ opacity: 1, x: 0 }}
                              transition={{ delay: 0.3 }}
                            >
                              <td className="p-3">
                                <div className="flex items-center gap-2">
                                  <span className="text-lg" aria-hidden="true">{RISK_ICONS[riskType]}</span>
                                  <span className="font-medium text-theme-text-primary">{RISK_LABELS[riskType]}</span>
                                </div>
                              </td>
                              <td className="p-3 text-right font-mono text-theme-text-primary">{orig.score}%</td>
                              <td className="p-3 text-right font-mono text-theme-text-primary">{sim.score}%</td>
                              <td className="p-3 text-right">
                                <span className={cn('font-mono font-bold px-2 py-0.5 rounded-full text-xs', comp.worsened ? 'bg-risk-high/10 text-risk-high' : 'bg-risk-low/10 text-risk-low')}>
                                  {comp.change > 0 ? '+' : ''}{comp.change}%
                                </span>
                              </td>
                              <td className="p-3 text-center">
                                <span className={cn('badge', `badge-risk-${orig.severity.toLowerCase()}`)}>
                                  {orig.severity}
                                </span>
                                {comp.worsened && sim.severity !== orig.severity && (
                                  <span className="ml-1 text-theme-accent text-xs" aria-hidden="true">→</span>
                                )}
                                {comp.worsened && sim.severity !== orig.severity && (
                                  <span className={cn('badge ml-1', `badge-risk-${sim.severity.toLowerCase()}`)}>
                                    {sim.severity}
                                  </span>
                                )}
                              </td>
                            </motion.tr>
                          );
                        })}
                      </tbody>
                    </table>
                  </div>
                </motion.div>
              )}

              {/* Summary */}
              {summary && (
                <motion.div className="card-organic p-4" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
                  <h3 className="font-heading text-h3 text-theme-text-primary mb-2 flex items-center gap-2">
                    <span aria-hidden="true">📋</span>
                    Summary
                  </h3>
                  <p className="text-body text-theme-text-secondary whitespace-pre-wrap">{summary}</p>
                </motion.div>
              )}

              {/* AI Explanation */}
              {aiExplanation && (
                <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }}>
                  <AIInsight explanation={aiExplanation as any} />
                </motion.div>
              )}

              {/* Controls */}
              <motion.div className="card-organic p-4 space-y-4" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.6 }}>
                <h3 className="font-heading text-h3 text-theme-text-primary flex items-center gap-2">
                  <span aria-hidden="true">🎛️</span>
                  Simulation Parameters
                </h3>

                <div className="space-y-4">
                  {SIMULATION_CONTROLS.map((control) => {
                    const rawValue = params[control.key];
                    const sliderValue = typeof rawValue === 'number' ? rawValue : Number(rawValue ?? 0);

                    return (
                      <Slider
                        key={control.key}
                        label={control.label}
                        min={control.min}
                        max={control.max}
                        step={control.step}
                        value={Number.isFinite(sliderValue) ? sliderValue : 0}
                        onChange={(value) => handleParamChange(control.key, value)}
                        unit={control.unit}
                        marks={control.marks}
                      />
                    );
                  })}

                  <div>
                    <label className="label">River Trend</label>
                    <Select
                      options={RIVER_TREND_OPTIONS}
                      value={riverTrend}
                      onChange={(event) => setRiverTrend(event.target.value as 'RISING' | 'FALLING' | 'STABLE' | '')}
                      placeholder="Select river trend"
                    />
                  </div>
                </div>
              </motion.div>
            </div>

            {/* Footer Actions */}
            <div className="p-4 border-t border-theme-divider flex items-center justify-end gap-3">
              <Button variant="ghost" onClick={handleReset} disabled={isRunning}>
                <RotateCcw className="w-4 h-4 mr-2" />
                Reset
              </Button>
              {simulatedRisks && (
                <>
                  <Button variant="secondary" onClick={() => navigator.clipboard.writeText(JSON.stringify({ params, comparison, summary }, null, 2))}>
                    <Save className="w-4 h-4 mr-2" />
                    Save Scenario
                  </Button>
                  <Button variant="secondary" onClick={() => navigator.share?.({ title: 'ClimateOps Simulation', text: formatScenarioDescription() })}>
                    <Share2 className="w-4 h-4 mr-2" />
                    Share
                  </Button>
                </>
              )}
              <Button variant="primary" onClick={handleRunSimulation} disabled={isRunning || Object.values(params).every((v) => v === 0) && !riverTrend}>
                {isRunning ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
                    Running...
                  </>
                ) : (
                  <>
                    <ChevronDown className="w-4 h-4 mr-2" />
                    Run Simulation
                  </>
                )}
              </Button>
            </div>
          </motion.aside>
        </>
      )}
    </AnimatePresence>
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