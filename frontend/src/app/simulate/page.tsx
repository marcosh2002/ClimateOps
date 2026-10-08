'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';
import { SearchAutocomplete } from '@/components/climate/SearchAutocomplete';
import { RiskGauge } from '@/components/climate/RiskGauge';
import { RiskBadge } from '@/components/climate/RiskBadge';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Slider } from '@/components/ui/Slider';
import { Select } from '@/components/ui/Select';
import { AIInsight } from '@/components/climate/AIInsight';
import { MapPin, Zap, ChevronDown, ChevronUp, Save, Share2, RotateCcw, ArrowLeft, X, Thermometer, Droplets, CloudRain, Sun, TrendingUp } from 'lucide-react';
import { useLocationStore, useSimulationStore } from '@/store';
import { api } from '@/lib/api';
import type { ClimateRiskDetail, SearchResult, SimulationParams, SimulationResponse } from '@/types';
import Link from 'next/link';
import { useRouter } from 'next/navigation';

type NumericSimulationKey = 'temperature_change' | 'humidity_change' | 'rainfall_change_pct' | 'river_level_change';

const SIMULATION_CONTROLS: Array<{
  key: NumericSimulationKey;
  label: string;
  unit: string;
  min: number;
  max: number;
  step: number;
  marks: { value: number; label: string }[];
  icon: typeof Thermometer;
}> = [
  {
    key: 'temperature_change',
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
    icon: Thermometer,
  },
  {
    key: 'humidity_change',
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
    icon: Droplets,
  },
  {
    key: 'rainfall_change_pct',
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
    icon: CloudRain,
  },
  {
    key: 'river_level_change',
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
    icon: Sun,
  },
];

const RIVER_TREND_OPTIONS = [
  { value: 'RISING', label: 'Rising ↗' },
  { value: 'STABLE', label: 'Stable →' },
  { value: 'FALLING', label: 'Falling ↘' },
];

const RISK_CONFIG = {
  heat: { label: 'Heat Risk', icon: Thermometer, color: 'risk-high' },
  flood: { label: 'Flood Risk', icon: Droplets, color: 'risk-medium' },
  water_stress: { label: 'Water Stress', icon: Sun, color: 'risk-low' },
  drought: { label: 'Drought Risk', icon: CloudRain, color: 'risk-high' },
};

export default function SimulatePage() {
  const router = useRouter();
  const { selectedLocation, setSelectedLocation, searchResults } = useLocationStore();
  const {
    isActive,
    simulatedRisks,
    comparison,
    summary,
    aiExplanation,
    clearResults,
  } = useSimulationStore();

  const [searchQuery, setSearchQuery] = useState('');
  const [params, setParams] = useState<SimulationParams>({});
  const [riverTrend, setRiverTrend] = useState<'RISING' | 'FALLING' | 'STABLE' | ''>('');
  const [isRunning, setIsRunning] = useState(false);
  const [showResults, setShowResults] = useState(false);
  const [locationData, setLocationData] = useState<{ location: any; risk: ClimateRiskDetail } | null>(null);

  const handleSearch = async (location: SearchResult) => {
    setSelectedLocation(location);
    setSearchQuery('');
    try {
      const data = await api.getClimateRisk(location.locationId);
      const riskDetails: ClimateRiskDetail = {
        heat: {
          score: data.risk.heatRisk,
          severity: data.risk.heatSeverity,
          factors: data.risk.contributingFactors.heat ?? [],
        },
        flood: {
          score: data.risk.floodRisk,
          severity: data.risk.floodSeverity,
          factors: data.risk.contributingFactors.flood ?? [],
        },
        water_stress: {
          score: data.risk.waterStressRisk,
          severity: data.risk.waterStressSeverity,
          factors: data.risk.contributingFactors.water_stress ?? [],
        },
        drought: {
          score: data.risk.droughtRisk,
          severity: data.risk.droughtSeverity,
          factors: data.risk.contributingFactors.drought ?? [],
        },
      };

      setLocationData({
        location: data.location,
        risk: riskDetails,
      });
      clearResults();
      setParams({});
      setRiverTrend('');
      setShowResults(false);
    } catch (err) {
      console.error('Failed to load location data:', err);
    }
  };

  const handleParamChange = (key: keyof SimulationParams, value: number) => {
    setParams((prev) => ({ ...prev, [key]: value }));
  };

  const handleRunSimulation = async () => {
    if (!locationData) return;
    setIsRunning(true);
    const simulationParams: SimulationParams = {
      ...params,
      river_trend: (riverTrend || undefined) as 'RISING' | 'FALLING' | 'STABLE' | undefined,
    };
    try {
      const result = await api.runSimulation(locationData.location.locationId, simulationParams);
      setShowResults(true);
    } catch (err) {
      console.error('Simulation failed:', err);
    } finally {
      setIsRunning(false);
    }
  };

  const handleReset = () => {
    clearResults();
    setParams({});
    setRiverTrend('');
    setShowResults(false);
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
    <div className="min-h-screen bg-theme-bg-primary">
      {/* Header */}
      <header className="sticky top-0 z-40 glass px-6 py-4 border-b border-theme-divider">
        <div className="container flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Link href="/" className="btn-ghost" onClick={(e) => { e.preventDefault(); router.back(); }}>
              <ArrowLeft className="w-5 h-5 mr-2" />
              Back
            </Link>
            <div>
              <h1 className="font-heading text-h2 text-theme-text-primary">What-If Simulation Lab</h1>
              <p className="text-sm text-theme-text-muted">Explore climate futures for any location</p>
            </div>
          </div>

          {locationData && (
            <div className="flex items-center gap-2">
              <Button variant="secondary" onClick={handleReset} disabled={isRunning}>
                <RotateCcw className="w-4 h-4 mr-2" />
                Reset
              </Button>
              {showResults && (
                <>
                  <Button variant="secondary" onClick={() => navigator.clipboard.writeText(JSON.stringify({ params, comparison, summary }, null, 2))}>
                    <Save className="w-4 h-4 mr-2" />
                    Save
                  </Button>
                  <Button variant="secondary" onClick={() => navigator.share?.({ title: 'ClimateOps Simulation', text: formatScenarioDescription() })}>
                    <Share2 className="w-4 h-4 mr-2" />
                    Share
                  </Button>
                </>
              )}
            </div>
          )}
        </div>
      </header>

      {/* Simulation Mode Banner */}
      {isActive && (
        <div className="bg-sun-100 dark:bg-sun-900 border-b border-sun-300 dark:border-sun-800 px-6 py-2 animate-pulse">
          <div className="container flex items-center justify-between text-sm">
            <span className="flex items-center gap-2 font-medium text-sun-800 dark:text-sun-200">
              <Zap className="w-4 h-4" />
              ⚠️ SIMULATION MODE ACTIVE — Data is hypothetical
            </span>
            <Button variant="ghost" size="sm" onClick={handleReset}>
              <X className="w-4 h-4 mr-1" />
              Exit
            </Button>
          </div>
        </div>
      )}

      <main className="container py-8 px-6">
        {!locationData ? (
          <motion.div
            className="max-w-2xl mx-auto text-center"
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <motion.div className="text-6xl mb-6 animate-pulse">🧪</motion.div>
            <motion.h1 className="font-display font-bold text-display text-theme-text-primary mb-4">
              Choose a Location to Simulate
            </motion.h1>
            <motion.p className="text-h3 text-theme-text-secondary mb-10 max-w-xl mx-auto">
              Select any location on Earth and explore how changing climate conditions would affect risk levels.
            </motion.p>

            <motion.div className="max-w-md mx-auto">
              <SearchAutocomplete
                value={searchQuery}
                onChange={setSearchQuery}
                onSearch={handleSearch}
                placeholder="Search location... (e.g., Mumbai, Dubai, London)"
                autoFocus
              />
              <p className="mt-4 text-sm text-theme-text-muted">
                Try: Mumbai, Dubai, London, Tokyo, New York, Sydney
              </p>
            </motion.div>

            <motion.div className="mt-12 grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
              {['Mumbai', 'Dubai', 'London', 'Tokyo'].map((city) => (
                <motion.button
                  key={city}
                  className="card-organic p-6 group"
                  onClick={() => { setSearchQuery(city); }}
                  whileHover={{ y: -4 }}
                >
                  <span className="text-3xl mb-2 block">🌍</span>
                  <span className="font-medium text-theme-text-primary">{city}</span>
                </motion.button>
              ))}
            </motion.div>
          </motion.div>
        ) : (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
          >
            {/* Location Header */}
            <motion.div className="mb-8 flex items-center justify-between">
              <div className="flex items-center gap-4">
                <Link href={`/climate/${locationData.location.locationId}`} className="btn-ghost">
                  <ArrowLeft className="w-5 h-5 mr-2" />
                  View Climate Detail
                </Link>
                <div>
                  <h2 className="font-heading text-h1 text-theme-text-primary">{locationData.location.city || locationData.location.district}, {locationData.location.state}</h2>
                  <p className="text-theme-text-muted">{locationData.location.latitude.toFixed(2)}°N, {locationData.location.longitude.toFixed(2)}°E</p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <span className="badge bg-sun-100 text-sun-700 dark:bg-sun-900 dark:text-sun-300 animate-pulse flex items-center gap-1">
                  <Zap className="w-3 h-3" />
                  SIMULATION
                </span>
              </div>
            </motion.div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Left Panel - Controls */}
              <motion.div className="lg:col-span-1 space-y-6" initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }}>
                <Card variant="elevated" padding="lg">
                  <h3 className="font-heading text-h3 text-theme-text-primary mb-6 flex items-center gap-2">
                    <Zap className="w-5 h-5" />
                    Simulation Parameters
                  </h3>
                  <div className="space-y-6">
                    {SIMULATION_CONTROLS.map((control) => (
                      <div key={control.key}>
                        <label className="flex items-center gap-2 label">
                          <control.icon className="w-4 h-4 text-theme-text-muted" />
                          {control.label}
                        </label>
                        <Slider
                          min={control.min}
                          max={control.max}
                          step={control.step}
                          value={Number(params[control.key] ?? 0)}
                          onChange={(value) => handleParamChange(control.key, value)}
                          unit={control.unit}
                          marks={control.marks}
                        />
                      </div>
                    ))}

                    <div>
                      <label className="label flex items-center gap-2">
                        <Sun className="w-4 h-4 text-theme-text-muted" />
                        River Trend
                      </label>
                      <Select
                        options={RIVER_TREND_OPTIONS}
                        value={riverTrend}
                        onChange={(event) => setRiverTrend(event.target.value as 'RISING' | 'FALLING' | 'STABLE' | '')}
                        placeholder="Select river trend"
                      />
                    </div>
                  </div>

                  <Button
                    variant="primary"
                    className="w-full mt-6 py-3 text-lg"
                    onClick={handleRunSimulation}
                    disabled={isRunning || (Object.values(params).every((v) => v === 0) && !riverTrend)}
                  >
                    {isRunning ? (
                      <>
                        <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
                        Running Simulation...
                      </>
                    ) : (
                      <>
                        <Zap className="w-5 h-5 mr-2" />
                        Run Simulation
                      </>
                    )}
                  </Button>
                </Card>

                {/* Current Conditions Summary */}
                <Card variant="outlined" padding="lg">
                  <h3 className="font-heading text-h3 text-theme-text-primary mb-4">Current Conditions</h3>
                  <div className="space-y-3">
                    {(['heat', 'flood', 'water_stress', 'drought'] as const).map((riskType) => {
                      const r = locationData.risk[riskType];
                      const config = RISK_CONFIG[riskType];
                      return (
                        <div key={riskType} className="flex items-center justify-between">
                          <span className="flex items-center gap-2 text-sm">
                            <config.icon className="w-4 h-4" style={{ color: `var(--${config.color})` }} />
                            <span className="font-medium text-theme-text-primary">{config.label}</span>
                          </span>
                          <RiskBadge score={r.score} label="" size="sm" />
                        </div>
                      );
                    })}
                  </div>
                </Card>
              </motion.div>

              {/* Right Panel - Comparison */}
              <motion.div className="lg:col-span-2 space-y-6" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }}>
                {/* Gauges Comparison */}
                <motion.div className="grid grid-cols-1 md:grid-cols-2 gap-4" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
                  <Card variant="elevated" padding="lg">
                    <h3 className="font-heading text-h3 text-theme-text-primary mb-4 text-center">CURRENT CONDITIONS</h3>
                    <RiskGauge
                      risks={locationData.risk}
                      size={280}
                      interactive={false}
                      showLabels={true}
                    />
                  </Card>
                  <Card variant="elevated" padding="lg">
                    <h3 className="font-heading text-h3 text-theme-text-primary mb-4 text-center">SIMULATED CONDITIONS</h3>
                    {simulatedRisks ? (
                      <RiskGauge
                        risks={simulatedRisks}
                        size={280}
                        interactive={false}
                        showLabels={true}
                      />
                    ) : (
                      <div className="h-64 flex items-center justify-center text-theme-text-muted">
                        Adjust parameters and run simulation
                      </div>
                    )}
                  </Card>
                </motion.div>

                {/* Comparison Table */}
                {comparison && (
                  <motion.div className="card-organic overflow-hidden" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
                    <div className="p-4 border-b border-theme-divider">
                      <h3 className="font-heading text-h3 text-theme-text-primary">Risk Comparison</h3>
                      <p className="text-body-sm text-theme-text-muted mt-1">{formatScenarioDescription()}</p>
                    </div>
                    <div className="overflow-x-auto">
                      <table className="w-full" role="table">
                        <thead>
                          <tr className="border-b border-theme-divider">
                            <th className="text-left p-3 font-medium text-theme-text-secondary">Risk</th>
                            <th className="text-right p-3 font-medium text-theme-text-secondary">Current</th>
                            <th className="text-right p-3 font-medium text-theme-text-secondary">Simulated</th>
                            <th className="text-right p-3 font-medium text-theme-text-secondary">Change</th>
                            <th className="text-center p-3 font-medium text-theme-text-secondary">Severity Shift</th>
                          </tr>
                        </thead>
                        <tbody>
                          {(['heat', 'flood', 'water_stress', 'drought'] as const).map((riskType) => {
                            const comp = comparison[riskType];
                            const orig = locationData.risk[riskType];
                            const sim = simulatedRisks?.[riskType];
                            const RiskIcon = RISK_CONFIG[riskType].icon;
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
                                    <RiskIcon className="w-5 h-5" style={{ color: `var(--${RISK_CONFIG[riskType].color})` }} />
                                    <span className="font-medium text-theme-text-primary">{RISK_CONFIG[riskType].label}</span>
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
                                    <>
                                      <TrendingUp className="w-4 h-4 mx-1 text-theme-accent inline" />
                                      <span className={cn('badge', `badge-risk-${sim.severity.toLowerCase()}`)}>
                                        {sim.severity}
                                      </span>
                                    </>
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
                  <motion.div className="card-organic p-4" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
                    <h3 className="font-heading text-h3 text-theme-text-primary mb-2 flex items-center gap-2">
                      <TrendingUp className="w-5 h-5" />
                      Simulation Summary
                    </h3>
                    <p className="text-body text-theme-text-secondary whitespace-pre-wrap">{summary}</p>
                  </motion.div>
                )}

                {/* AI Explanation */}
                {aiExplanation && (
                  <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
                    <AIInsight explanation={aiExplanation as any} />
                  </motion.div>
                )}
              </motion.div>
            </div>
          </motion.div>
        )}
      </main>
    </div>
  );
}