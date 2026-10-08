# ClimateOps Frontend — Design & Implementation Plan

## Design Philosophy

> **"Nature doesn't rush, yet everything is accomplished."** — Lao Tzu

The UI breathes with the planet. Every interaction feels organic, grounded, and alive. Data isn't displayed—it's revealed through living systems.

---

## Core Design Principles

| Principle | Expression |
|-----------|------------|
| **Living Data** | Risk levels drive ambient theme, not just badges |
| **Breathing Space** | Generous whitespace, organic flow, no rigid grids |
| **Nature as Metaphor** | Trees = resilience, Water = flow, Wind = change, Earth = stability |
| **Calm Urgency** | Critical states pulse gently, never scream |
| **Progressive Disclosure** | Overview → Detail → Action, never overwhelming |

---

## Color System — Nature-Inspired, Risk-Responsive

### Base Palette (Light Mode)
```css
:root {
  /* Earth & Soil */
  --earth-50: #faf6f1;
  --earth-100: #f3ebe0;
  --earth-200: #e6d5c4;
  --earth-300: #d4b89a;
  --earth-400: #c1956d;
  --earth-500: #a67c52;
  --earth-600: #8b6544;
  --earth-700: #735039;
  --earth-800: #5e4231;
  --earth-900: #4d372a;

  /* Forest & Foliage */
  --forest-50: #f0f5f0;
  --forest-100: #dce7dc;
  --forest-200: #b9cfba;
  --forest-300: #8db58d;
  --forest-400: #629563;
  --forest-500: #447a45;
  --forest-600: #366337;
  --forest-700: #2f4f2f;
  --forest-800: #2b422b;
  --forest-900: #253726;

  /* Water & Sky */
  --water-50: #eff6fa;
  --water-100: #d4e8f2;
  --water-200: #aad0e5;
  --water-300: #73b2d4;
  --water-400: #3d8fc0;
  --water-500: #1e6f9e;
  --water-600: #185780;
  --water-700: #164666;
  --water-800: #163b54;
  --water-900: #153245;

  /* Sun & Heat */
  --sun-50: #fff8ed;
  --sun-100: #ffefd3;
  --sun-200: #ffdfa6;
  --sun-300: #ffc76e;
  --sun-400: #ffaa33;
  --sun-500: #f5900e;
  --sun-600: #e0740a;
  --sun-700: #b8580c;
  --sun-800: #93460f;
  --sun-900: #783912;

  /* Semantic — Risk Reactive */
  --risk-low: var(--forest-500);
  --risk-medium: var(--sun-500);
  --risk-high: var(--sun-700);
  --risk-critical: #c02828;

  /* Neutral */
  --ink-900: #1a1a1a;
  --ink-700: #333;
  --ink-500: #555;
  --ink-300: #888;
  --ink-100: #ccc;
  --paper: #fefefe;
  --paper-alt: #fafafa;
}
```

### Risk-Responsive Theme System

```typescript
// Theme adapts to DOMINANT risk across the view
type RiskTheme = 'low' | 'medium' | 'high' | 'critical';

interface ThemeTokens {
  // Background shifts subtly
  bgPrimary: string;
  bgSecondary: string;
  bgAccent: string;

  // Text adapts for contrast
  textPrimary: string;
  textSecondary: string;
  textMuted: string;

  // Accent = dominant risk color
  accent: string;
  accentSoft: string;
  accentGlow: string;

  // Border & divider
  border: string;
  divider: string;

  // Shadow with risk hue
  shadow: string;
  shadowHover: string;
}

// Example: Heat-dominant view
const heatTheme: ThemeTokens = {
  bgPrimary: '#fff8ed',      // sun-50
  bgSecondary: '#ffefd3',    // sun-100
  bgAccent: '#ffdfa6',       // sun-200
  textPrimary: '#783912',    // sun-900
  textSecondary: '#93460f',  // sun-800
  textMuted: '#b8580c',      // sun-700
  accent: '#e0740a',         // sun-600
  accentSoft: 'rgba(224, 116, 10, 0.15)',
  accentGlow: 'rgba(224, 116, 10, 0.4)',
  border: '#ffc76e',         // sun-300
  divider: '#ffdfa6',        // sun-200
  shadow: 'rgba(224, 116, 10, 0.12)',
  shadowHover: 'rgba(224, 116, 10, 0.24)',
};
```

### Dark Mode — Night Forest
```css
@media (prefers-color-scheme: dark) {
  :root {
    --paper: #121812;
    --paper-alt: #1a221a;
    --ink-900: #f0f5f0;
    --ink-700: #dce7dc;
    --ink-500: #aab9aa;
    --ink-300: #7a8a7a;
    --ink-100: #4a5a4a;

    /* Risk themes deepen */
    --risk-critical: #e85d5d;
    --risk-high: #ffb340;
    --risk-medium: #ffd166;
    --risk-low: #6ec66e;
  }
}
```

---

## Typography — Organic, Readable, Expressive

| Role | Font | Scale | Use Case |
|------|------|-------|----------|
| **Display** | *Fraunces* (serif, variable) | clamp(2.5rem, 5vw, 4.5rem) | Hero, Location names, Risk scores |
| **Heading** | *DM Sans* (variable, 400-700) | clamp(1.5rem, 3vw, 2.5rem) | Section titles, Card headers |
| **Body** | *DM Sans* | 1rem / 1.6 | Primary content |
| **Body Small** | *DM Sans* | 0.875rem / 1.5 | Meta, labels, timestamps |
| **Mono** | *JetBrains Mono* | 0.875rem | Data values, coordinates, IDs |
| **Label** | *DM Sans* 500, uppercase, 0.05em tracking | 0.75rem | Risk badges, status pills |

### Fluid Type Scale (CSS)
```css
:root {
  --text-display: clamp(2.5rem, 5vw, 4.5rem);
  --text-h1: clamp(2rem, 4vw, 3rem);
  --text-h2: clamp(1.5rem, 3vw, 2.25rem);
  --text-h3: clamp(1.25rem, 2.5vw, 1.75rem);
  --text-body: 1rem;
  --text-sm: 0.875rem;
  --text-xs: 0.75rem;
  --text-mono: 0.875rem;
}
```

---

## Iconography & Illustration System

### Vector Animation Library (Lottie / Rive)

| Animation | Trigger | Duration | Loop |
|-----------|---------|----------|------|
| **Tree Breathing** | Ambient (always) | 8s | ∞ |
| **Water Ripple** | Hover on flood risk | 1.2s | Once |
| **Leaf Flutter** | Heat risk > 60 | 3s | ∞ |
| **Root Growth** | Water stress > 60 | 2s | Once |
| **Sun Pulse** | Critical heat | 2s | ∞ (slow) |
| **Rain Drops** | Heavy rain incident | 1.5s | ∞ |
| **River Flow** | Live monitoring active | 4s | ∞ |
| **Seed Sprout** | Simulation run complete | 2.5s | Once |
| **Compass Spin** | Location search | 0.8s | Once |
| **Horizon Shift** | Theme transition | 1.2s | Once |

### Static Illustrations (SVG, inline)
- **Location Cards**: Micro-landscape per region (mangroves for coast, dunes for desert, paddy for floodplains)
- **Empty States**: Sleeping tree, dry riverbed, waiting cloud
- **Loading**: Seed germinating → sapling → tree (3 stages)

---

## Layout System — Organic Grid

### Container Widths
```css
.container {
  width: 100%;
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 var(--space-6);
}

.container-narrow { max-width: 900px; }
.container-wide { max-width: 1600px; }
```

### Spacing Scale (Nature-Inspired Ratios)
```css
:root {
  --space-1: 0.25rem;   /* 4px  */
  --space-2: 0.5rem;    /* 8px  */
  --space-3: 0.75rem;   /* 12px */
  --space-4: 1rem;      /* 16px */
  --space-5: 1.25rem;   /* 20px */
  --space-6: 1.5rem;    /* 24px */
  --space-8: 2rem;      /* 32px */
  --space-10: 2.5rem;   /* 40px */
  --space-12: 3rem;     /* 48px */
  --space-16: 4rem;     /* 64px */
  --space-20: 5rem;     /* 80px */
  --space-24: 6rem;     /* 96px */
}
```

### Grid — CSS Grid with Organic Flow
```css
.grid {
  display: grid;
  gap: var(--space-6);
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  align-items: start;
}

.grid-dense {
  grid-auto-flow: dense;
}

.grid-card { grid-column: span 1; }
.grid-card-wide { grid-column: span 2; }
.grid-card-full { grid-column: 1 / -1; }
```

---

## Component Architecture

### Atomic Components

#### 1. RiskBadge — Living Indicator
```tsx
interface RiskBadgeProps {
  score: number;        // 0-100
  label: string;        // "Heat Risk"
  size: 'sm' | 'md' | 'lg';
  animate?: boolean;    // Pulse if critical
  showTrend?: 'up' | 'down' | 'stable';
}

// Visual: Circular progress ring + score + label
// Ring color = risk level
// Critical: subtle pulse animation (scale 1 → 1.02 → 1)
// Trend: tiny arrow with water/leaf icon
```

#### 2. RiskGauge — Radial Visualization
```tsx
interface RiskGaugeProps {
  risks: {
    heat: number;
    flood: number;
    waterStress: number;
    drought: number;
  };
  size: number;        // 200-400px
  interactive?: boolean; // Hover to highlight segment
}

// Visual: 4-segment ring, each segment = risk type
// Segments grow clockwise from top
// Hover: segment expands, tooltip with factors
// Center: overall risk level + dominant risk icon
```

#### 3. LocationCard — Organic Tile
```tsx
interface LocationCardProps {
  location: Location;
  risk?: RiskAssessment;
  incident?: Incident;
  variant: 'search' | 'monitored' | 'incident' | 'simulation';
  onSelect: () => void;
}

// Structure:
// ┌─────────────────────────────────────┐
// │  🌿 Micro-landscape illustration    │  ← 120px height, clipped
// ├─────────────────────────────────────┤
// │  📍 City, State                     │
// │  ⚠️ Dominant risk badge (if any)    │
// ├─────────────────────────────────────┤
// │  [RiskGauge mini]  or  [4 RiskBadges]│
// └─────────────────────────────────────┘

// Hover: illustration subtly animates (wind, ripple)
// Click: expands into detail drawer
```

#### 4. ThemeProvider — Context for Risk-Reactive UI
```tsx
interface ThemeContextValue {
  theme: ThemeTokens;
  dominantRisk: RiskType | null;
  setDominantRisk: (risk: RiskType | null) => void;
  transitionTheme: (newTheme: ThemeTokens) => void;
}

// Wraps entire app
// Listens to WebSocket risk updates
// Smoothly transitions CSS vars (1.2s ease-out)
```

---

## Page Specifications

### 1. Landing / Home — "The Canopy"

**Route**: `/`
**Purpose**: Entry point, global search, system status overview

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│    🌿 [Animated canopy illustration - trees swaying gently]    │
│                                                                 │
│    ┌─────────────────────────────────────────────────────┐     │
│    │  🔍  Search any location on Earth...                │     │
│    │     [Autocomplete: Dubai, London, Mumbai, Tokyo...] │     │
│    └─────────────────────────────────────────────────────┘     │
│                                                                 │
│    ┌──────────────────┐  ┌──────────────────┐  ┌────────────┐  │
│    │  🌍 CLIMATE INTEL │  │  🚨 INDIA OPS    │  │  🧪 SIMULATE │  │
│    │  Global risk      │  │  Live incidents │  │  What-if     │  │
│    │  analysis         │  │  4 active now   │  │  scenarios   │  │
│    └──────────────────┘  └──────────────────┘  └────────────┘  │
│                                                                 │
│    [Live pulse indicator]  Monitoring 126 locations  🟢        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Animations**:
- Canopy: continuous slow sway (8s loop)
- Search focus: roots grow downward from input
- Card hover: illustration comes alive (wind/rain/sun)
- Stats counter: counts up on mount

---

### 2. Climate Intelligence — Location Detail

**Route**: `/climate/:locationId`
**Purpose**: Deep risk analysis for any global location

```
┌─────────────────────────────────────────────────────────────────┐
│  ← Back                    📍 Mumbai, Maharashtra, India       │
│                          19.07°N, 72.88°E    [Share] [Simulate] │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────┐  ┌────────────────────────────────────┐  │
│  │                  │  │  🌡️  HEAT RISK        82%  HIGH    │  │
│  │   [Large         │  │  ████████████████████░░░░░░░░░░    │  │
│  │    RiskGauge     │  │  Factors: Temp 38°C, Humidity 78%  │  │
│  │    320px]        │  │  Trend: ↗ Rising 3% / 24h          │  │
│  │                  │  │  Source: IMD, OpenWeather          │  │
│  └──────────────────┘  ├────────────────────────────────────┤  │
│                        │  🌊  FLOOD RISK       12%  LOW      │  │
│  ┌──────────────────┐  │  ████░░░░░░░░░░░░░░░░░░░░░░░░░░    │  │
│  │  🌿 AI INSIGHT   │  │  Factors: Minimal rainfall         │  │
│  │  ┌────────────┐  │  │  Trend: → Stable                   │  │
│  │  │ "High heat │  │  ├────────────────────────────────────┤  │
│  │  │  risk is   │  │  │  💧  WATER STRESS     76%  HIGH    │  │
│  │  │  driven by │  │  │  ████████████████████████░░░░░░░  │  │
│  │  │  sustained │  │  │  Factors: Low rainfall, high temp  │  │
│  │  │  temps..." │  │  │  Trend: ↗ Rising 8% / week         │  │
│  │  └────────────┘  │  ├────────────────────────────────────┤  │
│  │  [Regenerate]    │  │  ☀️  DROUGHT RISK      54%  MEDIUM  │  │
│  └──────────────────┘  │  ████████████████░░░░░░░░░░░░░░░    │  │
│                        │  Factors: Soil moisture declining    │  │
│                        │  Trend: ↗ Rising 12% / month         │  │
│                        └────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  📈 24-HOUR TREND                    📊 7-DAY FORECAST   │  │
│  │  [Mini sparklines for each risk type]                    │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Theme Behavior**:
- Page background = dominant risk theme (heat → warm, flood → cool blue, etc.)
- RiskGauge segments animate on load (grow from 0)
- AI Insight appears with typewriter effect
- Sparklines draw themselves (stroke-dashoffset)

**Interactions**:
- Click risk row → expands factor details
- "Simulate" button → opens simulation drawer
- Location header: subtle parallax on scroll

---

### 3. What-If Simulation — "The Laboratory"

**Route**: `/climate/:locationId/simulate` (or drawer/modal)
**Purpose**: Explore climate futures

```
┌─────────────────────────────────────────────────────────────────┐
│  🧪  What-If Simulation — Mumbai                          [×]  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────┐  ┌─────────────────────────────────┐  │
│  │  CURRENT CONDITIONS │  │  SIMULATED CONDITIONS           │  │
│  │  ┌───────────────┐  │  │  ┌───────────────┐              │  │
│  │  │   RiskGauge   │  │  │  │   RiskGauge   │              │  │
│  │  │   (live)      │  │  │  │   (preview)   │              │  │
│  │  └───────────────┘  │  │  └───────────────┘              │  │
│  │                     │  │                                 │  │
│  │  Temp: 38°C         │  │  Temp: 41°C    [+3°C slider]   │  │
│  │  Rainfall: 5mm      │  │  Rainfall: 3.5mm [-30% slider] │  │
│  │  Humidity: 78%      │  │  Humidity: 82%                  │  │
│  │  River: 12m stable  │  │  River: 11.5m ↘                 │  │
│  └─────────────────────┘  └─────────────────────────────────┘  │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  COMPARISON                                              │   │
│  │  ┌─────────┬──────────┬──────────┬────────┬────────────┐ │   │
│  │  │ Risk    │ Current  │ Simulated│ Change │ Severity   │ │   │
│  │  ├─────────┼──────────┼──────────┼────────┼────────────┤ │   │
│  │  │ 🌡️ Heat │ 82% HIGH │ 94% CRIT │ +12% ↗ │ HIGH→CRIT  │ │   │
│  │  │ 🌊 Flood│ 12% LOW  │ 14% LOW  │ +2% ↗  │ —          │ │   │
│  │  │ 💧 Water│ 76% HIGH │ 88% CRIT │ +12% ↗ │ HIGH→CRIT  │ │   │
│  │  │ ☀️ Drought│54% MED  │ 68% HIGH │ +14% ↗ │ MED→HIGH   │ │   │
│  │  └─────────┴──────────┴──────────┴────────┴────────────┘ │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  🌿 AI EXPLANATION                                       │   │
│  │  "A 3°C rise pushes heat risk into critical territory.  │   │
│  │   Water stress escalates dramatically due to increased  │   │
│  │   evaporation. Drought risk climbs as soil moisture...  │   │
│  │   [Priority actions: Reduce exposure, Increase cooling] │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  [Run Simulation]  [Reset]  [Save Scenario]  [Share]          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Animations**:
- Sliders: smooth drag, gauge updates in real-time (debounced 150ms)
- Comparison table: rows slide in with stagger
- RiskGauge: smooth segment transitions
- AI Explanation: streaming text effect

**Controls**:
- Temperature: -10°C to +10°C (step 0.5)
- Rainfall: -80% to +200% (step 5%)
- Humidity: -30% to +20% (step 1%)
- River Level: -5m to +10m (step 0.5m)
- River Trend: [RISING, STABLE, FALLING] selector
- Add/Remove Alert: dropdown with types

---

### 4. India Emergency Command Center — "The Watchtower"

**Route**: `/emergency`
**Purpose**: Live monitoring dashboard for India

```
┌─────────────────────────────────────────────────────────────────┐
│  🚨  INDIA EMERGENCY COMMAND CENTER                    [⚙️] [🌙] │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐            │
│  │ 🔴 ACTIVE    │ │ 🟠 HIGH RISK │ │ 🟢 MONITORED │            │
│  │    04        │ │    08        │ │    126       │            │
│  │  incidents   │ │  locations   │ │  locations   │            │
│  └──────────────┘ └──────────────┘ └──────────────┘            │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  🗺️  LIVE MAP — India (SVG/Canvas, WebGL)                │  │
│  │  • Pulsing dots = active incidents                       │  │
│  │  • Ring color = severity, size = risk score              │  │
│  │  • Hover → tooltip, Click → select                       │  │
│  │  • Time slider: 24h replay                               │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  ACTIVE INCIDENTS                              [Filter ▼] │  │
│  │  ┌────┬────────────┬────────┬─────────┬──────┬────────┐   │  │
│  │  │ 🔴 │ FLOOD      │ Assam  │ CRITICAL│ 94%  │ 10:45  │   │  │
│  │  │ 🔴 │ HEAVY RAIN │ W.Bengal│ CRITICAL│ 91% │ 10:45  │   │  │
│  │  │ 🟠 │ HEAT       │ Rajasthan│ HIGH   │ 82%  │ 10:40  │   │  │
│  │  │ 🟠 │ FLOOD      │ Bihar   │ HIGH   │ 78%  │ 10:35  │   │  │
│  │  └────┴────────────┴────────┴─────────┴──────┴────────┘   │  │
│  │  [Auto-refresh: 30s]  [WebSocket: 🟢 Connected]            │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Map Layer Details**:
- Base: Topographic (terrain) or Satellite toggle
- Incident markers: Organic shapes (not pins) — flood = water droplet, heat = sunburst, drought = cracked earth
- Pulse animation: `scale(1) → scale(1.3) → opacity(0)` over 2s, staggered
- Risk zones: Subtle overlay polygons (district-level) with risk hue at 10% opacity
- Time scrubber: Bottom, shows incident evolution

**Live Updates** (WebSocket/SSE):
- New incident: marker grows from center with ripple
- Risk change: ring expands/contracts, color shifts
- Resolution: marker fades, dissolves into leaf particles
- Connection status: top-right, green pulse = live

---

### 5. Incident Detail — "The Incident Report"

**Route**: `/emergency/incidents/:incidentId`
**Purpose**: Full incident timeline, evidence, AI explanation

```
┌─────────────────────────────────────────────────────────────────┐
│  ← Back    INCIDENT #INC-1024    🔴 CRITICAL    [Live] [Export] │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────┐  ┌─────────────────────────────┐  │
│  │  📍 Guwahati, Assam     │  │  🌡️ HEAT      34%  LOW      │  │
│  │  🌊 FLOOD • CRITICAL    │  │  🌊 FLOOD      94%  CRITICAL │  │
│  │  Risk Score: 94%        │  │  💧 WATER      67%  HIGH     │  │
│  │  Status: ACTIVE         │  │  ☀️ DROUGHT    23%  LOW      │  │
│  │  Created: 10:35 AM      │  │                             │  │
│  │  Next Check: 10:45 AM   │  │  [Large RiskGauge - Flood]  │  │
│  │  Source: IMD + CWC      │  │                             │  │
│  └─────────────────────────┘  └─────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  ⚠️  WHY IS THIS AN EMERGENCY?                           │  │
│  │  ✅ Heavy rainfall detected (126mm / 24h)                │  │
│  │  ✅ River level rising (48.2m → 48.7m)                   │  │
│  │  ✅ Official flood warning active                        │  │
│  │  ✅ Flood risk above critical threshold (94%)            │  │
│  │  ✅ Risk increased from 91% → 94% in last 5 min          │  │
│  │                                                          │  │
│  │  [Each checkmark animates in sequentially on load]       │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  🌿 AI SITUATION REPORT                                   │  │
│  │  "Critical flooding in Guwahati driven by sustained      │  │
│  │   monsoon rainfall exceeding 120mm. Brahmaputra river    │  │
│  │   rising rapidly with official warning in effect.        │  │
│  │                                                          │  │
│  │   IMMEDIATE PRIORITIES:                                   │  │
│  │   1. Evacuate low-lying areas along river                │  │
│  │   2. Deploy water rescue teams to Chandmari, Silpukhuri  │  │
│  │   3. Activate relief shelters at 5 identified sites      │  │
│  │   4. Monitor embankment integrity at 3 vulnerable points │  │
│  │                                                          │  │
│  │   POTENTIAL IMPACT: 50,000+ people affected if           │  │
│  │   embankment breaches. Next 6 hours critical.            │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  📈 LIVE TIMELINE                    📊 RISK TRAJECTORY  │  │
│  │  10:35 ✅ Official warning detected    [Sparkline: 82→94]│  │
│  │  10:35 ✅ Incident created             ▲                   │  │
│  │  10:36 ✅ Risk calculated: 91%         │                   │  │
│  │  10:40 ✅ New data received            │                   │  │
│  │  10:40 ⚠ Risk increased: 91% → 94%    │                   │  │
│  │  10:45 ✅ Monitoring continues          ▼                  │  │
│  │                                                          │  │
│  │  [Timeline auto-scrolls, new entries slide in from bottom]│  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Theme**: Flood-dominant → water theme (cool blues, ripple animations)
**Animations**:
- Timeline: new entries slide up with fade
- Risk trajectory: line draws itself
- AI Report: streaming text
- Checkmarks: draw-in animation (stroke-dashoffset)

---

### 6. Simulation Mode Banner (Global)

```
┌─────────────────────────────────────────────────────────────────┐
│  ⚠️  SIMULATION MODE ACTIVE — Data is hypothetical             │
│  [Exit Simulation]                                              │
└─────────────────────────────────────────────────────────────────┘
```

- Fixed top banner, amber background
- Subtle pulse animation
- Appears on ALL pages when simulation mode active

---

## User Flows

### Flow 1: Global Climate Intelligence
```
Landing → Search "Tokyo" → Climate Detail (Tokyo)
    → View risks → Read AI insight → Click "Simulate"
    → Adjust sliders → See comparison → Read AI explanation
    → Save scenario / Share → Back to detail → New search
```

### Flow 2: India Emergency Monitoring
```
Landing → "India Emergency Ops" card → Command Center
    → See active incidents on map → Click incident
    → Incident Detail → Read AI report → View timeline
    → WebSocket updates → Risk changes → Theme shifts
    → Incident resolves → Marker dissolves → Back to map
```

### Flow 3: What-If Exploration
```
Climate Detail → "Simulate" → Simulation Drawer
    → Adjust temperature +3°C → Gauge updates live
    → Adjust rainfall -30% → Comparison table updates
    → Click "Run Simulation" → Seed sprout animation
    → AI explanation streams → Save scenario
    → Close → Back to Climate Detail (real data restored)
```

### Flow 4: Theme Transition (Cross-cutting)
```
Any Page → WebSocket risk update → Dominant risk changes
    → ThemeProvider.transitionTheme(newTheme)
    → CSS vars animate (1.2s ease-out)
    → Components re-render with new tokens
    → Illustrations swap (tree → sun → cloud → water)
    → No layout shift, pure visual transformation
```

---

## Responsive Breakpoints

| Breakpoint | Width | Layout Adjustments |
|------------|-------|-------------------|
| Mobile | < 640px | Single column, bottom sheet for details, map full-screen |
| Tablet | 640-1024px | 2-col grid, side drawer for incident detail |
| Desktop | 1024-1440px | Full grid, persistent sidebars |
| Wide | > 1440px | 3-col map + list + detail, expanded gauges |

---

## Animation Choreography

### Entrance Animations (Page Load)
```typescript
const pageEntrance = {
  // Staggered, organic reveal
  header: { delay: 0, duration: 0.6, ease: 'ease-out' },
  hero: { delay: 0.1, duration: 0.8, ease: 'ease-out' },
  cards: { delay: 0.2, stagger: 0.08, duration: 0.5 },
  gauges: { delay: 0.4, duration: 1.2, ease: 'ease-out-circ' }, // draw
  aiInsight: { delay: 0.8, duration: 1.5 }, // typewriter
};
```

### Micro-Interactions
| Trigger | Animation | Duration |
|---------|-----------|----------|
| Button hover | Scale 1.02, shadow deepen | 150ms |
| Card hover | Lift 4px, illustration animates | 200ms |
| Risk badge critical | Pulse (scale 1→1.03→1) | 2s loop |
| Theme change | CSS var transition | 1.2s |
| Tab switch | Cross-fade + slide | 300ms |
| Drawer open | Slide + backdrop blur | 250ms |
| Toast/notification | Slide from bottom, bounce | 400ms |

### Reduced Motion
```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

---

## State Management Architecture

### Stores (Zustand / Jotai / Signals)

```typescript
// stores/themeStore.ts
interface ThemeState {
  dominantRisk: RiskType | null;
  theme: ThemeTokens;
  isDark: boolean;
  transitionTheme: (risk: RiskType) => void;
  toggleDark: () => void;
}

// stores/incidentStore.ts
interface IncidentState {
  activeIncidents: Incident[];
  selectedIncident: Incident | null;
  timeline: IncidentObservation[];
  subscribe: () => void; // WebSocket
  unsubscribe: () => void;
}

// stores/simulationStore.ts
interface SimulationState {
  isActive: boolean;
  originalObservation: EnvironmentalObservation | null;
  simulatedObservation: EnvironmentalObservation | null;
  comparison: ComparisonData | null;
  aiExplanation: AIExplanation | null;
  setParams: (params: SimulationParams) => void;
  run: () => Promise<void>;
  reset: () => void;
}

// stores/locationStore.ts
interface LocationState {
  searchQuery: string;
  searchResults: Location[];
  selectedLocation: Location | null;
  monitoredLocations: Location[];
  search: (query: string) => Promise<void>;
  select: (location: Location) => void;
}
```

---

## Data Fetching & Caching (TanStack Query / SWR)

```typescript
// queries.ts
const queryKeys = {
  climate: (locationId: string) => ['climate', locationId],
  climateHistory: (locationId: string, hours: number) => ['climate', locationId, 'history', hours],
  incidents: () => ['incidents'],
  incident: (id: string) => ['incidents', id],
  incidentTimeline: (id: string) => ['incidents', id, 'timeline'],
  monitoredLocations: () => ['monitored-locations'],
  simulation: (id: string) => ['simulation', id],
};

// Stale times
const STALE_TIME = {
  climate: 5 * 60 * 1000,        // 5 min
  incidents: 30 * 1000,          // 30 sec
  monitoredLocations: 60 * 1000, // 1 min
  simulation: 0,                 // never stale (user-driven)
};
```

---

## WebSocket / SSE Integration

```typescript
// hooks/useIncidentSocket.ts
function useIncidentSocket() {
  const { activeIncidents, setIncidents, updateIncident, removeIncident } = useIncidentStore();

  useEffect(() => {
    const ws = new WebSocket(`${WS_URL}/incidents`);

    ws.onmessage = (event) => {
      const msg = JSON.parse(event.data);

      switch (msg.type) {
        case 'incident_created':
          setIncidents(prev => [...prev, msg.data]);
          playSound('new-incident'); // subtle chime
          break;
        case 'incident_updated':
          updateIncident(msg.data.incidentId, msg.data);
          if (msg.data.riskScore >= 80) pulseTheme(msg.data.type);
          break;
        case 'incident_resolved':
          removeIncident(msg.data.incidentId);
          playSound('resolve'); // gentle tone
          break;
        case 'risk_update':
          // Update location risk in background
          break;
        case 'summary_update':
          updateSummary(msg.data);
          break;
      }
    };

    return () => ws.close();
  }, []);
}
```

---

## Accessibility (WCAG 2.1 AA)

| Requirement | Implementation |
|-------------|----------------|
| Color Contrast | All text ≥ 4.5:1, risk badges ≥ 3:1 (large text) |
| Focus Visible | Custom focus rings using risk accent color |
| Screen Readers | Live regions for incident updates, ARIA labels on gauges |
| Keyboard Nav | Full keyboard support, skip links, focus trap in drawers |
| Reduced Motion | Respects `prefers-reduced-motion` |
| Color Blind Safe | Risk levels use shape + pattern + color (not color alone) |
| Language | `lang="en"`, translatable strings |

### Risk Badge Accessibility Pattern
```tsx
<div class="risk-badge" role="img" aria-label={`Heat risk: 82 percent, HIGH`}>
  <svg class="ring" viewBox="0 0 48 48" aria-hidden="true">
    <circle class="bg" cx="24" cy="24" r="20" />
    <circle class="progress" cx="24" cy="24" r="20"
      stroke-dasharray="125.6" stroke-dashoffset="22.6" />
  </svg>
  <span class="score">82%</span>
  <span class="label">HIGH</span>
  <span class="trend up" aria-label="Rising 3%">↗</span>
</div>
```

---

## Performance Budget

| Metric | Target |
|--------|--------|
| Initial JS (gzipped) | < 120 KB |
| Initial CSS (gzipped) | < 30 KB |
| LCP | < 2.5s |
| FID | < 100ms |
| CLS | < 0.1 |
| Lottie animations | < 50 KB each, lazy-loaded |
| Images | WebP/AVIF, responsive, lazy |

---

## Tech Stack Recommendation

| Layer | Choice | Rationale |
|-------|--------|-----------|
| **Framework** | Next.js 14 (App Router) | RSC, streaming, SEO, edge-ready |
| **Language** | TypeScript (strict) | Type safety for risk data |
| **Styling** | Tailwind CSS + CSS Variables | Utility-first + dynamic theming |
| **Animations** | Framer Motion + Lottie/Rive | Declarative, performant, vector |
| **Charts** | Recharts (SVG) or uPlot (Canvas) | Sparklines, risk trajectories |
| **Maps** | MapLibre GL + custom style | Vector tiles, offline-capable |
| **State** | Zustand + TanStack Query | Simple global + server state |
| **Forms** | React Hook Form + Zod | Validation, simulation params |
| **Icons** | Lucide React + Custom SVG | Consistent, tree-shakeable |
| **Testing** | Vitest + Playwright | Unit + E2E |
| **Lint/Format** | Biome (fast, all-in-one) | Speed, consistency |

---

## Implementation Phases

### Phase 1: Foundation (Week 1-2)
- [ ] Next.js 14 setup with Tailwind, TypeScript
- [ ] Design tokens (colors, spacing, typography) as CSS vars
- [ ] ThemeProvider with risk-reactive context
- [ ] Base components: Button, Card, Badge, Input, Tooltip
- [ ] Animation primitives (Framer Motion variants)
- [ ] Lottie/Rive integration setup
- [ ] Storybook for component documentation

### Phase 2: Core Layout & Navigation (Week 2)
- [ ] Responsive layout components (Container, Grid, Sidebar)
- [ ] Navigation shell (header, breadcrumbs, theme toggle)
- [ ] Landing page with animated canopy
- [ ] Global search with autocomplete
- [ ] Simulation mode banner

### Phase 3: Climate Intelligence Pages (Week 3-4)
- [ ] Location Detail page with RiskGauge
- [ ] RiskBadge, RiskGauge components
- [ ] AI Insight panel with streaming text
- [ ] Sparklines / trend charts
- [ ] Theme transition system (CSS var animation)
- [ ] Micro-landscape illustrations per region

### Phase 4: Simulation Laboratory (Week 4)
- [ ] Simulation drawer/modal
- [ ] Interactive sliders with live gauge preview
- [ ] Comparison table with animated rows
- [ ] AI explanation streaming
- [ ] Save/Share scenario functionality

### Phase 5: India Emergency Command Center (Week 5-6)
- [ ] Live map (MapLibre GL) with custom style
- [ ] Incident markers with organic shapes
- [ ] Pulse animations, time scrubber
- [ ] Incident list with live updates
- [ ] WebSocket/SSE integration
- [ ] Connection status indicator

### Phase 6: Incident Detail & Timeline (Week 6)
- [ ] Incident Detail page
- [ ] "Why Emergency" checklist with draw-in animation
- [ ] AI Situation Report with streaming
- [ ] Live timeline with auto-scroll
- [ ] Risk trajectory chart
- [ ] Export/Share functionality

### Phase 7: Polish & Performance (Week 7)
- [ ] Dark mode refinement
- [ ] Reduced motion support
- [ ] Accessibility audit
- [ ] Performance optimization (code splitting, lazy loading)
- [ ] Cross-browser testing
- [ ] Animation refinement
- [ ] Documentation

---

## Illustration & Animation Asset List

### Lottie/Rive Files Needed
```
animations/
├── canopy-breathing.json          # Landing hero (loop)
├── tree-sway.json                 # Location cards (loop)
├── water-ripple.json              # Flood hover/active
├── leaf-flutter.json              # Heat risk (loop)
├── root-growth.json               # Water stress (once)
├── sun-pulse.json                 # Critical heat (loop)
├── rain-drops.json                # Heavy rain (loop)
├── river-flow.json                # Live monitoring (loop)
├── seed-sprout.json               # Simulation complete (once)
├── compass-spin.json              # Search (once)
├── horizon-shift.json             # Theme transition (once)
├── checkmark-draw.json            # Why emergency (once each)
├── marker-bloom.json              # New incident (once)
├── marker-dissolve.json           # Resolved incident (once)
└── loading-germinate.json         # Page load (loop)
```

### Static SVG Illustrations
```
illustrations/
├── micro-landscapes/
│   ├── coastal-mangroves.svg
│   ├── desert-dunes.svg
│   ├── floodplain-paddy.svg
│   ├── mountain-forest.svg
│   ├── urban-canopy.svg
│   └── river-delta.svg
├── empty-states/
│   ├── sleeping-tree.svg
│   ├── dry-riverbed.svg
│   └── waiting-cloud.svg
├── icons/
│   ├── risk-heat.svg
│   ├── risk-flood.svg
│   ├── risk-water-stress.svg
│   ├── risk-drought.svg
│   └── incident-types/ (12 variants)
└── ui/
    ├── leaf-bullet.svg
    ├── water-drop-bullet.svg
    └── sun-ray-bullet.svg
```

---

## Handoff Checklist for Development

- [ ] Design tokens exported as JSON + CSS vars + Figma variables
- [ ] Component specs in Storybook with all states
- [ ] Animation specs with timing curves (cubic-bezier values)
- [ ] Illustration assets as optimized SVG + Lottie JSON
- [ ] Accessibility annotations on all components
- [ ] Responsive breakpoints documented
- [ ] Dark mode variants for all tokens
- [ ] Risk theme tokens for all 4 risk types × 4 severities
- [ ] Icon system with naming convention
- [ ] Sound assets for notifications (optional)

---

## Future Enhancements (Post-MVP)

1. **3D Globe View** — Three.js globe with risk heatmap
2. **AR Overlay** — Mobile camera view with risk data
3. **Voice Briefing** — TTS for incident reports
4. **Community Layer** — User reports, photos, verification
5. **Historical Replay** — Seasonal risk animation
6. **Multi-language** — Hindi, Bengali, Tamil, etc.
7. **Offline PWA** — Service worker, background sync
8. **Authority Dashboard** — Role-based views for govt/NGOs

---

## Success Metrics

| Metric | Target |
|--------|--------|
| Time to Interactive | < 3s |
| Theme transition smoothness | 60fps, no layout shift |
| WebSocket reconnection | < 2s |
| Animation frame drops | 0 on mid-range devices |
| Accessibility score | 100 (Lighthouse) |
| Bundle size (initial) | < 150 KB gzipped |
| User task completion | > 90% (usability testing) |

---

*"The clearest way into the Universe is through a forest wilderness."* — John Muir

This frontend embodies that clarity: data as nature, urgency as growth, complexity as canopy.