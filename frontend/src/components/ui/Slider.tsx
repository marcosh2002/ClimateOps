'use client';

import { InputHTMLAttributes, forwardRef, useId } from 'react';
import { cn } from '@/lib/utils';

export interface SliderProps extends Omit<InputHTMLAttributes<HTMLInputElement>, 'type' | 'onChange' | 'value'> {
  label?: string;
  min?: number;
  max?: number;
  step?: number;
  value: number;
  onChange: (value: number) => void;
  unit?: string;
  showValue?: boolean;
  marks?: { value: number; label: string }[];
}

export const Slider = forwardRef<HTMLInputElement, SliderProps>(
  ({ className, label, min = 0, max = 100, step = 1, value, onChange, unit, showValue = true, marks, id, ...props }, ref) => {
    const sliderId = useId();
    const inputId = id || sliderId;
    const percentage = ((value - min) / (max - min)) * 100;

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
      onChange(Number(e.target.value));
    };

    return (
      <div className={cn('w-full', className)}>
        {label && (
          <div className="flex items-center justify-between mb-2">
            <label htmlFor={inputId} className="label mb-0">
              {label}
            </label>
            {showValue && (
              <span className="text-sm font-mono text-theme-accent bg-theme-accent/10 px-2 py-0.5 rounded-full">
                {value}{unit ? ` ${unit}` : ''}
              </span>
            )}
          </div>
        )}
        <div className="relative">
          <div
            className="absolute top-1/2 left-0 right-0 h-1 -translate-y-1/2 bg-theme-bg-accent rounded-full overflow-hidden"
            aria-hidden="true"
          >
            <div
              className="h-full bg-theme-accent rounded-full transition-all duration-fast"
              style={{ width: `${percentage}%` }}
            />
          </div>
          <input
            ref={ref}
            type="range"
            id={inputId}
            min={min}
            max={max}
            step={step}
            value={value}
            onChange={handleChange}
            className={cn(
              'relative w-full h-8 appearance-none bg-transparent cursor-pointer',
              'focus:outline-none focus-visible:ring-2 focus-visible:ring-theme-accent focus-visible:ring-offset-2 focus-visible:ring-offset-theme-bg-primary',
              'disabled:opacity-50 disabled:cursor-not-allowed'
            )}
            {...props}
          />
          {marks && (
            <div className="flex justify-between mt-2 text-xs text-theme-text-muted">
              {marks.map((mark) => (
                <span key={mark.value} className="font-mono">
                  {mark.label}
                </span>
              ))}
            </div>
          )}
        </div>
      </div>
    );
  }
);

Slider.displayName = 'Slider';