import { HTMLAttributes, forwardRef } from 'react';
import { cn } from '@/lib/utils';
import type { RiskLevel } from '@/types';

export interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  variant?: 'default' | 'risk' | 'success' | 'warning' | 'danger' | 'info';
  riskLevel?: RiskLevel;
  size?: 'sm' | 'md' | 'lg';
  dot?: boolean;
}

export const Badge = forwardRef<HTMLSpanElement, BadgeProps>(
  ({ className, variant = 'default', riskLevel, size = 'md', dot = false, children, ...props }, ref) => {
    const baseStyles = 'inline-flex items-center gap-1.5 font-medium rounded-full transition-colors duration-fast';

    const variants = {
      default: 'bg-theme-bg-accent text-theme-text-primary border border-theme-border',
      risk: 'bg-theme-accent/10 text-theme-accent border border-theme-accent/20',
      success: 'bg-forest-100 text-forest-700 dark:bg-forest-900 dark:text-forest-300',
      warning: 'bg-sun-100 text-sun-700 dark:bg-sun-900 dark:text-sun-300',
      danger: 'bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300',
      info: 'bg-water-100 text-water-700 dark:bg-water-900 dark:text-water-300',
    };

    const riskVariants: Record<RiskLevel, string> = {
      LOW: 'bg-forest-100 text-forest-700 dark:bg-forest-900 dark:text-forest-300',
      MEDIUM: 'bg-sun-100 text-sun-700 dark:bg-sun-900 dark:text-sun-300',
      HIGH: 'bg-sun-200 text-sun-800 dark:bg-sun-800 dark:text-sun-200',
      CRITICAL: 'bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300 animate-pulse-critical',
    };

    const sizes = {
      sm: 'px-2 py-0.5 text-xs',
      md: 'px-3 py-1 text-xs',
      lg: 'px-4 py-1.5 text-sm',
    };

    let variantClass = variants[variant];
    if (variant === 'risk' && riskLevel) {
      variantClass = riskVariants[riskLevel];
    }

    return (
      <span
        ref={ref}
        className={cn(baseStyles, variantClass, sizes[size], className)}
        {...props}
      >
        {dot && (
          <span
            className={cn(
              'w-1.5 h-1.5 rounded-full flex-shrink-0',
              variant === 'risk' && riskLevel
                ? riskVariants[riskLevel].replace('bg-', 'bg-').replace('text-', 'bg-')
                : variants[variant].replace('bg-', 'bg-').replace('text-', 'bg-')
            )}
            aria-hidden="true"
          />
        )}
        {children}
      </span>
    );
  }
);

Badge.displayName = 'Badge';