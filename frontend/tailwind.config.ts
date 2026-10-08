/** @type {import('tailwindcss').Config} */
const themeColor = (variable: string) => ({ opacityValue }: { opacityValue?: string }) => {
  const opacity = Number(opacityValue);
  return opacityValue === undefined || !Number.isFinite(opacity)
    ? `var(${variable})`
    : `color-mix(in srgb, var(${variable}) ${opacity * 100}%, transparent)`;
};

module.exports = {
  darkMode: 'class',
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
    './src/stories/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        // Earth & Soil
        earth: {
          50: '#faf6f1',
          100: '#f3ebe0',
          200: '#e6d5c4',
          300: '#d4b89a',
          400: '#c1956d',
          500: '#a67c52',
          600: '#8b6544',
          700: '#735039',
          800: '#5e4231',
          900: '#4d372a',
          950: '#2a1e16',
        },
        // Forest & Foliage
        forest: {
          50: '#f0f5f0',
          100: '#dce7dc',
          200: '#b9cfba',
          300: '#8db58d',
          400: '#629563',
          500: '#447a45',
          600: '#366337',
          700: '#2f4f2f',
          800: '#2b422b',
          900: '#253726',
          950: '#131d14',
        },
        // Water & Sky
        water: {
          50: '#eff6fa',
          100: '#d4e8f2',
          200: '#aad0e5',
          300: '#73b2d4',
          400: '#3d8fc0',
          500: '#1e6f9e',
          600: '#185780',
          700: '#164666',
          800: '#163b54',
          900: '#153245',
          950: '#0b1a25',
        },
        // Sun & Heat
        sun: {
          50: '#fff8ed',
          100: '#ffefd3',
          200: '#ffdfa6',
          300: '#ffc76e',
          400: '#ffaa33',
          500: '#f5900e',
          600: '#e0740a',
          700: '#b8580c',
          800: '#93460f',
          900: '#783912',
          950: '#401d06',
        },
        // Semantic Risk Colors
        risk: {
          low: themeColor('--risk-low'),
          medium: themeColor('--risk-medium'),
          high: themeColor('--risk-high'),
          critical: themeColor('--risk-critical'),
        },
        // Theme-aware semantic colors
        theme: {
          bg: {
            primary: themeColor('--theme-bg-primary'),
            secondary: themeColor('--theme-bg-secondary'),
            accent: themeColor('--theme-bg-accent'),
          },
          text: {
            primary: themeColor('--theme-text-primary'),
            secondary: themeColor('--theme-text-secondary'),
            muted: themeColor('--theme-text-muted'),
          },
          accent: {
            DEFAULT: themeColor('--theme-accent'),
            soft: 'var(--theme-accent-soft)',
            glow: 'var(--theme-accent-glow)',
          },
          border: themeColor('--theme-border'),
          divider: themeColor('--theme-divider'),
          shadow: 'var(--theme-shadow)',
          'shadow-hover': 'var(--theme-shadow-hover)',
        },
      },
      fontFamily: {
        display: ['var(--font-fraunces)', 'Georgia', 'serif'],
        heading: ['var(--font-dm-sans)', 'system-ui', 'sans-serif'],
        body: ['var(--font-dm-sans)', 'system-ui', 'sans-serif'],
        mono: ['var(--font-jetbrains-mono)', 'monospace'],
      },
      fontSize: {
        'display': ['clamp(2.5rem, 5vw, 4.5rem)', { lineHeight: '1.1', letterSpacing: '-0.02em' }],
        'h1': ['clamp(2rem, 4vw, 3rem)', { lineHeight: '1.2', letterSpacing: '-0.01em' }],
        'h2': ['clamp(1.5rem, 3vw, 2.25rem)', { lineHeight: '1.25' }],
        'h3': ['clamp(1.25rem, 2.5vw, 1.75rem)', { lineHeight: '1.3' }],
        'body': ['1rem', { lineHeight: '1.6' }],
        'body-sm': ['0.875rem', { lineHeight: '1.5' }],
        'xs': ['0.75rem', { lineHeight: '1.5' }],
        'mono': ['0.875rem', { lineHeight: '1.5' }],
      },
      spacing: {
        '1': '0.25rem',
        '2': '0.5rem',
        '3': '0.75rem',
        '4': '1rem',
        '5': '1.25rem',
        '6': '1.5rem',
        '8': '2rem',
        '10': '2.5rem',
        '12': '3rem',
        '16': '4rem',
        '20': '5rem',
        '24': '6rem',
      },
      borderRadius: {
        'organic': '1.5rem',
        'organic-sm': '1rem',
        'organic-lg': '2rem',
        'organic-xl': '3rem',
      },
      boxShadow: {
        'organic': 'var(--theme-shadow)',
        'organic-hover': 'var(--theme-shadow-hover)',
        'glow': '0 0 20px var(--theme-accent-glow)',
        'glow-lg': '0 0 40px var(--theme-accent-glow)',
      },
      transitionDuration: {
        'theme': '1200ms',
        'fast': '150ms',
        'normal': '200ms',
        'slow': '300ms',
      },
      transitionTimingFunction: {
        'organic': 'cubic-bezier(0.4, 0, 0.2, 1)',
        'bounce': 'cubic-bezier(0.68, -0.55, 0.265, 1.55)',
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'pulse-critical': 'pulse-critical 2s ease-in-out infinite',
        'sway': 'sway 8s ease-in-out infinite',
        'ripple': 'ripple 1.2s ease-out',
        'flutter': 'flutter 3s ease-in-out infinite',
        'grow': 'grow 2s ease-out',
        'draw': 'draw 1.5s ease-out forwards',
        'fade-in-up': 'fade-in-up 0.5s ease-out forwards',
        'slide-in-right': 'slide-in-right 0.3s ease-out forwards',
        'slide-in-bottom': 'slide-in-bottom 0.4s ease-out forwards',
        'scale-in': 'scale-in 0.2s ease-out forwards',
      },
      keyframes: {
        'pulse-critical': {
          '0%, 100%': { transform: 'scale(1)', opacity: '1' },
          '50%': { transform: 'scale(1.03)', opacity: '0.8' },
        },
        sway: {
          '0%, 100%': { transform: 'rotate(-1deg)' },
          '50%': { transform: 'rotate(1deg)' },
        },
        ripple: {
          '0%': { transform: 'scale(0)', opacity: '0.5' },
          '100%': { transform: 'scale(2)', opacity: '0' },
        },
        flutter: {
          '0%, 100%': { transform: 'rotate(-3deg) translateX(-2px)' },
          '50%': { transform: 'rotate(3deg) translateX(2px)' },
        },
        grow: {
          '0%': { transform: 'scale(0.8)', opacity: '0' },
          '100%': { transform: 'scale(1)', opacity: '1' },
        },
        draw: {
          '0%': { strokeDashoffset: '100%' },
          '100%': { strokeDashoffset: '0%' },
        },
        'fade-in-up': {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        'slide-in-right': {
          '0%': { opacity: '0', transform: 'translateX(20px)' },
          '100%': { opacity: '1', transform: 'translateX(0)' },
        },
        'slide-in-bottom': {
          '0%': { opacity: '0', transform: 'translateY(100%)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        'scale-in': {
          '0%': { opacity: '0', transform: 'scale(0.95)' },
          '100%': { opacity: '1', transform: 'scale(1)' },
        },
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'gradient-conic': 'conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))',
        'canopy': "url('/illustrations/canopy-pattern.svg')",
      },
    },
  },
  plugins: [],
}