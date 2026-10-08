'use client';

import { createContext, useContext, useEffect, useMemo, ReactNode } from 'react';
import { useThemeStore } from '@/store';
import { getThemeClass } from '@/lib/utils';
import type { RiskType } from '@/types';

interface ThemeContextValue {
  dominantRisk: RiskType | null;
  isCritical: boolean;
  isDark: boolean;
  themeClass: string;
  setDominantRisk: (risk: RiskType | null, isCritical?: boolean) => void;
  toggleDark: () => void;
}

const ThemeContext = createContext<ThemeContextValue | null>(null);

export function ThemeProvider({ children }: { children: ReactNode }) {
  const { dominantRisk, isCritical, isDark, setDominantRisk, toggleDark } = useThemeStore();

  const themeClass = useMemo(() => {
    const base = isDark ? 'dark' : '';
    const risk = dominantRisk ? getThemeClass(dominantRisk, isCritical) : '';
    return [base, risk].filter(Boolean).join(' ');
  }, [dominantRisk, isCritical, isDark]);

  useEffect(() => {
    const root = document.documentElement;
    root.classList.remove('dark', ...Array.from(root.classList).filter((name) => name.startsWith('theme-')));
    themeClass.split(' ').filter(Boolean).forEach((name) => root.classList.add(name));
  }, [themeClass]);

  return (
    <ThemeContext.Provider
      value={{
        dominantRisk,
        isCritical,
        isDark,
        themeClass,
        setDominantRisk,
        toggleDark,
      }}
    >
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
}