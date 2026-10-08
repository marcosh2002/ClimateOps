import { forwardRef, ButtonHTMLAttributes } from 'react';
import { cn } from '@/lib/utils';

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  loading?: boolean;
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = 'primary', size = 'md', loading, disabled, children, ...props }, ref) => {
    const baseStyles = 'inline-flex items-center justify-center gap-2 font-medium transition-all duration-fast focus-visible:ring-2 focus-visible:ring-theme-accent focus-visible:ring-offset-2 focus-visible:ring-offset-theme-bg-primary disabled:opacity-50 disabled:cursor-not-allowed';

    const variants = {
      primary: 'bg-theme-accent text-white hover:bg-theme-accent/90 active:bg-theme-accent active:scale-[0.98]',
      secondary: 'bg-theme-bg-accent text-theme-text-primary hover:bg-theme-bg-accent/80 border border-theme-border',
      ghost: 'bg-transparent hover:bg-theme-accent/10 text-theme-text-secondary',
      danger: 'bg-risk-critical text-white hover:bg-risk-critical/90',
    };

    const sizes = {
      sm: 'rounded-organic-sm px-3 py-1.5 text-xs',
      md: 'rounded-organic-sm px-5 py-2.5 text-sm',
      lg: 'rounded-organic px-6 py-3 text-base',
    };

    return (
      <button
        ref={ref}
        className={cn(baseStyles, variants[variant], sizes[size], className)}
        disabled={disabled || loading}
        {...props}
      >
        {loading && (
          <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24" aria-hidden="true">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="3" fill="none" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
          </svg>
        )}
        {children}
      </button>
    );
  }
);

Button.displayName = 'Button';