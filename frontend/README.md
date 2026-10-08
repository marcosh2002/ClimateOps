# ClimateOps Frontend

Next.js 14 frontend for ClimateOps — Climate Intelligence & Emergency Response Platform.

## Features

- **Global Climate Intelligence**: Search any location, view risk assessments (heat, flood, water stress, drought)
- **What-If Simulation**: Interactive sliders with live gauge preview, AI explanations
- **India Emergency Command Center**: Live map with WebSocket updates, incident timeline
- **Nature-Reactive UI**: Theme shifts with dominant risk, organic animations throughout
- **Accessible**: WCAG 2.1 AA compliant, reduced motion support

## Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript (strict)
- **Styling**: Tailwind CSS + CSS Variables
- **Animations**: Framer Motion + Lottie
- **Maps**: MapLibre GL
- **State**: Zustand + TanStack Query
- **Forms**: React Hook Form + Zod
- **Charts**: Recharts
- **Lint/Format**: Biome

## Quick Start

### Prerequisites

- Node.js 20+
- Backend running on `http://localhost:8000`

### Installation

```bash
cd frontend
npm install
cp .env.example .env.local
# Edit .env.local with your API URL
npm run dev
```

Open http://localhost:3000

### Development Commands

```bash
npm run dev        # Start dev server
npm run build      # Production build
npm run start      # Start production server
npm run lint       # Lint with Biome
npm run lint:fix   # Auto-fix lint issues
npm run format     # Format with Biome
npm run typecheck  # TypeScript check
npm run test       # Run Vitest tests
npm run test:ui    # Vitest UI
npm run storybook  # Storybook
```

## Project Structure

```
frontend/
├── src/
│   ├── app/                    # Next.js App Router pages
│   │   ├── layout.tsx          # Root layout with providers
│   │   ├── page.tsx            # Landing page
│   │   ├── climate/[locationId]/page.tsx    # Climate detail
│   │   ├── emergency/page.tsx              # Command center
│   │   ├── emergency/incidents/[incidentId]/page.tsx
│   │   └── simulate/page.tsx               # What-if simulation
│   ├── components/
│   │   ├── providers/          # ThemeProvider, etc.
│   │   ├── ui/                 # Atomic components (Button, Card, etc.)
│   │   ├── climate/            # RiskBadge, RiskGauge, SearchAutocomplete
│   │   ├── emergency/          # IncidentCard, IncidentDetail
│   │   ├── simulation/         # SimulationDrawer
│   │   ├── maps/               # EmergencyMap
│   │   ├── charts/             # Sparklines, charts
│   │   └── layout/             # Layout components
│   ├── lib/
│   │   ├── api.ts              # API client
│   │   └── utils.ts            # Utility functions
│   ├── store/                  # Zustand stores
│   ├── hooks/                  # Custom React hooks
│   ├── types/                  # TypeScript types
│   ├── styles/                 # Global styles
│   └── utils/                  # Helper functions
├── public/
│   ├── illustrations/          # Static SVG illustrations
│   └── animations/             # Lottie/Rive animations
└── .storybook/                 # Storybook config
```

## Design System

### Color Themes (Risk-Reactive)

| Risk | Light Theme | Dark Theme |
|------|-------------|------------|
| Heat | Warm amber (`sun-*`) | Deep amber |
| Flood | Cool blue (`water-*`) | Deep blue |
| Water Stress | Earth tones (`earth-*`) | Dark earth |
| Drought | Warm ochre (`sun-*`) | Dark ochre |

Theme transitions animate CSS variables over 1.2s.

### Typography

- **Display**: Fraunces (variable serif)
- **Body/UI**: DM Sans (variable sans)
- **Mono**: JetBrains Mono

### Spacing Scale

`4, 8, 12, 16, 20, 24, 32, 40, 48, 64, 80, 96` (4px base)

### Border Radius

`organic-sm: 1rem`, `organic: 1.5rem`, `organic-lg: 2rem`, `organic-xl: 3rem`

## Key Components

### RiskBadge
Circular progress ring with score, severity badge, and trend indicator.

```tsx
<RiskBadge score={82} label="Heat Risk" size="lg" animate showTrend="up" />
```

### RiskGauge
4-segment radial gauge showing all risk types with interactive hover.

```tsx
<RiskGauge risks={climateRiskDetail} size={320} interactive />
```

### SimulationDrawer
Slide-over panel with dual gauges, live sliders, comparison table, AI explanation.

### EmergencyMap
MapLibre GL map with pulsing organic incident markers, time scrubber.

## WebSocket Integration

Real-time updates via WebSocket at `/api/monitoring/ws/incidents`:

```typescript
// Message types
type WSMessage =
  | { type: 'incident_created'; data: Incident }
  | { type: 'incident_updated'; data: Partial<Incident> & { incidentId: string } }
  | { type: 'incident_resolved'; data: { incidentId: string } }
  | { type: 'summary_update'; data: IncidentSummaryResponse }
  | { type: 'risk_update'; data: { locationId: string; risk: RiskAssessment } };
```

## Accessibility

- Semantic HTML with ARIA labels
- Focus visible rings using theme accent
- Live regions for incident updates
- `prefers-reduced-motion` respected
- Color-blind safe (shape + pattern + color)
- Keyboard navigation throughout

## Animation Performance

- Framer Motion for layout animations
- CSS transitions for theme changes (1.2s)
- Lottie for complex illustrations
- `will-change` hints on animated elements
- Reduced motion: all animations disabled

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | Backend API base URL | `http://localhost:8000` |
| `NEXT_PUBLIC_WS_URL` | WebSocket URL | `ws://localhost:8000` |
| `NEXT_PUBLIC_SIMULATION_MODE` | Enable simulation features | `true` |

## Deployment

### Vercel (Recommended)

```bash
vercel --prod
```

Set environment variables in Vercel dashboard.

### Docker

```dockerfile
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
EXPOSE 3000
CMD ["node", "server.js"]
```

Enable `output: 'standalone'` in `next.config.js`.

## Testing

```bash
# Unit tests
npm run test

# E2E tests (Playwright)
npm run test:e2e

# Visual regression (Storybook + Chromatic)
npm run storybook
```

## Contributing

1. Run `npm run lint:fix` before committing
2. Follow TypeScript strict mode
3. Use semantic commits
4. Test with reduced motion enabled
5. Verify dark mode and all risk themes

## License

MIT