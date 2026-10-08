'use client';

import { useState } from 'react';
import { motion, useReducedMotion } from 'framer-motion';
import {
  Activity,
  ArrowDownRight,
  ArrowRight,
  ArrowUpRight,
  Globe2,
  Leaf,
  Moon,
  Search,
  Sun,
  Waves,
} from 'lucide-react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { SearchAutocomplete } from '@/components/climate/SearchAutocomplete';
import { useTheme } from '@/components/providers/ThemeProvider';
import { useLocationStore } from '@/store';
import type { SearchResult } from '@/types';

const WORKSPACES = [
  {
    eyebrow: '01 / EXPLORE',
    title: 'Climate intelligence',
    description: 'Understand heat, flood, drought, and water stress for places around the world.',
    icon: Globe2,
    className: 'workspace-forest',
    href: '#location-search',
    action: 'Search a location',
  },
  {
    eyebrow: '02 / RESPOND',
    title: 'Emergency operations',
    description: 'Track emerging incidents and changing conditions across India.',
    icon: Activity,
    className: 'workspace-amber',
    href: '/emergency',
    action: 'Open operations',
  },
  {
    eyebrow: '03 / PLAN',
    title: 'Scenario lab',
    description: 'Test how changing weather and river conditions could shift risk.',
    icon: Waves,
    className: 'workspace-blue',
    href: '/simulate',
    action: 'Run a scenario',
  },
];

const EXAMPLE_LOCATIONS = ['Mumbai', 'Delhi', 'Bengaluru', 'Chennai', 'Kolkata'];

export default function LandingPage() {
  const { setSelectedLocation } = useLocationStore();
  const { isDark, toggleDark } = useTheme();
  const router = useRouter();
  const [searchQuery, setSearchQuery] = useState('');
  const shouldReduceMotion = useReducedMotion();

  const handleSearch = (location: SearchResult) => {
    setSelectedLocation(location);
    setSearchQuery('');
    router.push(`/climate/${location.locationId}`);
  };

  const revealMotion = shouldReduceMotion
    ? {}
    : { initial: { opacity: 0, y: 18 }, whileInView: { opacity: 1, y: 0 }, viewport: { once: true, amount: 0.2 } };

  return (
    <main className="min-h-screen overflow-hidden">
      <header className="site-header">
        <nav className="site-nav" aria-label="Main navigation">
          <Link href="/" className="brand" aria-label="ClimateOps home">
            <span className="brand-mark"><Leaf size={17} strokeWidth={2.2} /></span>
            <span>climate<span className="brand-light">ops</span></span>
          </Link>

          <div className="nav-links">
            <a href="#workspaces" className="nav-link">Platform</a>
            <Link href="/emergency" className="nav-link">Live operations</Link>
            <Link href="/simulate" className="nav-link">Scenario lab</Link>
          </div>

          <div className="nav-actions">
            <button
              type="button"
              className="icon-button"
              onClick={toggleDark}
              aria-label={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
            >
              {isDark ? <Sun size={17} /> : <Moon size={17} />}
            </button>
            <Link href="#location-search" className="nav-cta">
              Explore platform <ArrowUpRight size={15} />
            </Link>
          </div>
        </nav>
      </header>

      <section className="hero-section">
        <div className="hero-grid" aria-hidden="true" />
        <div className="hero-layout">
          <motion.div
            className="hero-copy"
            initial={shouldReduceMotion ? false : { opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.65, ease: [0.22, 1, 0.36, 1] }}
          >
            <div className="eyebrow"><span className="eyebrow-dot" /> CLIMATE INTELLIGENCE, IN CONTEXT</div>
            <h1>
              See the signal.<br />
              <span>Shape what comes next.</span>
            </h1>
            <p className="hero-description">
              A clearer view of climate risk — from the first warning to the next decision.
            </p>

            <div id="location-search" className="hero-search">
              <SearchAutocomplete
                value={searchQuery}
                onChange={setSearchQuery}
                onSearch={handleSearch}
                placeholder="Search a city, district or region"
              />
              <div className="search-hint"><Search size={13} /> Try a location</div>
            </div>

            <div className="location-chips" aria-label="Popular locations">
              {EXAMPLE_LOCATIONS.map((location) => (
                <button key={location} type="button" onClick={() => setSearchQuery(location)}>
                  {location}
                </button>
              ))}
            </div>
          </motion.div>

          <motion.div
            className="landscape-wrap"
            initial={shouldReduceMotion ? false : { opacity: 0, scale: 0.97 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.8, delay: 0.12, ease: [0.22, 1, 0.36, 1] }}
          >
            <LandscapeIllustration animate={!shouldReduceMotion} />
            <div className="landscape-label">
              <span className="landscape-label-icon"><Waves size={15} /></span>
              <span><strong>Living systems</strong><small>Connected by climate</small></span>
              <span className="landscape-label-status"><i /> LIVE</span>
            </div>
            <motion.div
              className="insight-card"
              animate={shouldReduceMotion ? undefined : { y: [0, -5, 0] }}
              transition={{ duration: 5, repeat: Infinity, ease: 'easeInOut' }}
            >
              <div className="insight-card-top"><span>RISK OUTLOOK</span><ArrowUpRight size={14} /></div>
              <div className="insight-card-score">4 dimensions</div>
              <div className="insight-card-bottom"><span>Heat · flood · water · drought</span></div>
            </motion.div>
          </motion.div>
        </div>

        <div className="signal-strip">
          <div><span className="signal-icon signal-green"><Globe2 size={15} /></span><span><strong>Global</strong><small>location intelligence</small></span></div>
          <div><span className="signal-icon signal-red"><span className="signal-pulse" /></span><span><strong>India</strong><small>emergency operations</small></span></div>
          <div><span className="signal-icon signal-blue"><Waves size={15} /></span><span><strong>4</strong><small>climate risk dimensions</small></span></div>
          <span className="signal-footnote">Updates as conditions change</span>
        </div>
      </section>

      <section id="workspaces" className="workspace-section">
        <div className="section-heading">
          <motion.div {...revealMotion}>
            <p className="section-kicker">ONE CONNECTED WORKSPACE</p>
            <h2>From early signal to<br className="desktop-break" /> confident action.</h2>
          </motion.div>
          <motion.p className="section-intro" {...revealMotion}>
            Move from a global view to local detail, live response, and practical what-if planning.
          </motion.p>
        </div>

        <div className="workspace-grid">
          {WORKSPACES.map((workspace, index) => {
            const Icon = workspace.icon;
            return (
              <motion.article
                key={workspace.title}
                className={`workspace-card ${workspace.className}`}
                {...revealMotion}
                transition={{ duration: 0.45, delay: index * 0.08 }}
                whileHover={shouldReduceMotion ? undefined : { y: -5 }}
              >
                <div className="workspace-card-top">
                  <span className="workspace-icon"><Icon size={19} /></span>
                  <span className="workspace-eyebrow">{workspace.eyebrow}</span>
                </div>
                <div>
                  <h3>{workspace.title}</h3>
                  <p>{workspace.description}</p>
                </div>
                <Link href={workspace.href} className="workspace-link">
                  {workspace.action}<ArrowRight size={15} />
                </Link>
                <div className="workspace-watermark" aria-hidden="true"><Icon size={100} strokeWidth={0.75} /></div>
              </motion.article>
            );
          })}
        </div>
      </section>

      <section className="principles-section">
        <motion.div className="principles-copy" {...revealMotion}>
          <p className="section-kicker">BUILT FOR CLARITY</p>
          <h2>Complex climate data.<br /><span>Human decisions.</span></h2>
          <p>Transparent risk signals and useful context — designed to help teams understand change, not just watch another dashboard.</p>
          <Link href="/emergency" className="text-link">See live operations <ArrowRight size={15} /></Link>
        </motion.div>
        <motion.div className="principles-list" {...revealMotion}>
          <Principle icon={<Activity size={18} />} title="Explainable by design" text="See the factors behind each risk score." />
          <Principle icon={<Waves size={18} />} title="Connected to place" text="Read weather, water, and risk in local context." />
          <Principle icon={<ArrowDownRight size={18} />} title="Made for next steps" text="Explore scenarios and prioritize a response." />
        </motion.div>
      </section>

      <footer className="site-footer">
        <Link href="/" className="brand"><span className="brand-mark"><Leaf size={16} /></span><span>climate<span className="brand-light">ops</span></span></Link>
        <p>Climate intelligence for a changing world.</p>
        <span>© 2026 ClimateOps</span>
      </footer>
    </main>
  );
}

function LandscapeIllustration({ animate }: { animate: boolean }) {
  return (
    <div className="landscape-art" aria-hidden="true">
      <svg viewBox="0 0 720 520" role="presentation" preserveAspectRatio="xMidYMid slice">
        <defs>
          <linearGradient id="sky" x1="0" x2="0" y1="0" y2="1">
            <stop offset="0%" stopColor="#dfece1" />
            <stop offset="100%" stopColor="#f1ead6" />
          </linearGradient>
          <linearGradient id="river" x1="0" x2="1" y1="0" y2="1">
            <stop offset="0%" stopColor="#6a9e98" />
            <stop offset="100%" stopColor="#a9c7b8" />
          </linearGradient>
          <linearGradient id="hill" x1="0" x2="0" y1="0" y2="1">
            <stop offset="0%" stopColor="#8ba987" />
            <stop offset="100%" stopColor="#426c59" />
          </linearGradient>
          <linearGradient id="hillFar" x1="0" x2="0" y1="0" y2="1">
            <stop offset="0%" stopColor="#b5c3a2" />
            <stop offset="100%" stopColor="#829b7c" />
          </linearGradient>
        </defs>
        <rect width="720" height="520" fill="url(#sky)" />
        <circle cx="535" cy="116" r="52" fill="#f7f0d7" opacity=".75" />
        <path d="M0 255 91 179l63 57 88-105 92 115 86-76 118 89 82-71 100 80v252H0Z" fill="url(#hillFar)" opacity=".65" />
        <path d="M0 307q130-104 259-19 118 80 233-7t228 16v223H0Z" fill="#789477" />
        <path d="M0 355q114-78 233 5t226-2q125-91 261-7v160H0Z" fill="url(#hill)" />
        <path d="M358 520c-18-77 14-115 31-164 17-48-13-91-12-140-42 49-67 96-51 143 17 51-8 95-19 161Z" fill="url(#river)" />
        <path d="M355 520c-12-77 20-115 37-164 16-47-11-91-14-130" fill="none" stroke="#d5e2ce" strokeWidth="4" opacity=".8" />
        {animate && (
          <motion.path
            d="M355 510c-10-70 22-111 37-157 16-48-10-87-13-125"
            fill="none"
            stroke="#e6f0df"
            strokeWidth="2"
            strokeDasharray="9 18"
            animate={{ strokeDashoffset: [0, -54] }}
            transition={{ duration: 5, repeat: Infinity, ease: 'linear' }}
          />
        )}
        <g fill="#315744">
          <path d="m78 309 24-74 25 74h-15v45H93v-45Z" />
          <path d="m134 324 19-58 20 58h-12v35h-15v-35Z" />
          <path d="m570 308 25-78 26 78h-16v48h-18v-48Z" />
          <path d="m620 331 20-62 21 62h-13v37h-16v-37Z" />
          <path d="m500 352 20-61 21 61h-13v36h-16v-36Z" />
        </g>
        <g fill="#56785e">
          <circle cx="102" cy="229" r="12" /><circle cx="92" cy="243" r="13" /><circle cx="111" cy="246" r="13" />
          <circle cx="594" cy="223" r="13" /><circle cx="583" cy="239" r="14" /><circle cx="604" cy="241" r="13" />
          <circle cx="522" cy="281" r="11" /><circle cx="513" cy="295" r="12" /><circle cx="531" cy="296" r="12" />
        </g>
        <g fill="#f2d99c" opacity=".82">
          <circle cx="176" cy="371" r="2" /><circle cx="213" cy="405" r="2" /><circle cx="470" cy="382" r="2" />
          <circle cx="266" cy="350" r="2" /><circle cx="552" cy="408" r="2" /><circle cx="87" cy="398" r="2" />
        </g>
        {animate && (
          <motion.g
            animate={{ rotate: [0, 2, 0, -2, 0] }}
            transition={{ duration: 7, repeat: Infinity, ease: 'easeInOut' }}
            style={{ transformOrigin: '102px 255px' }}
          >
            <circle cx="102" cy="229" r="12" fill="#56785e" />
            <circle cx="92" cy="243" r="13" fill="#56785e" />
            <circle cx="111" cy="246" r="13" fill="#56785e" />
          </motion.g>
        )}
        <path d="M0 455q104-33 193 0t181 0q94-30 178 1t168 1v63H0Z" fill="#355a49" opacity=".55" />
      </svg>
      <div className="landscape-overlay" />
      <div className="map-marker marker-one"><span /></div>
      <div className="map-marker marker-two"><span /></div>
      <div className="map-marker marker-three"><span /></div>
    </div>
  );
}

function Principle({ icon, title, text }: { icon: React.ReactNode; title: string; text: string }) {
  return (
    <div className="principle-row">
      <span className="principle-icon">{icon}</span>
      <span><strong>{title}</strong><small>{text}</small></span>
      <ArrowRight className="principle-arrow" size={16} />
    </div>
  );
}
