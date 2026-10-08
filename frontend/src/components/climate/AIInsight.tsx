'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { RefreshCw } from 'lucide-react';
import type { AIExplanation } from '@/types';

interface AIInsightProps {
  explanation: AIExplanation | null;
  title?: string;
  isLoading?: boolean;
  error?: string | null;
  onRegenerate?: () => void;
  className?: string;
}

export function AIInsight({
  explanation,
  title = 'AI Climate Insight',
  isLoading = false,
  error,
  onRegenerate,
  className,
}: AIInsightProps) {
  const items = [
    { label: 'Summary', content: explanation?.summary, icon: '📋' },
    { label: 'Key Factors', content: explanation?.key_factors.join(', '), icon: '🔍' },
    { label: 'Recommendations', content: explanation?.recommendations.join('; '), icon: '💡' },
    { label: 'Potential Impacts', content: explanation?.potential_impacts.join('; '), icon: '⚠️' },
  ].filter((item) => item.content);

  return (
    <Card variant="elevated" className={cn('overflow-hidden', className)}>
      <CardHeader className="flex items-center justify-between">
        <CardTitle className="flex items-center gap-2">
          <span className="text-2xl" aria-hidden="true">🌿</span>
          {title}
        </CardTitle>
        {onRegenerate && (
          <Button variant="ghost" size="sm" onClick={onRegenerate} disabled={isLoading}>
            <RefreshCw className={cn('w-4 h-4', isLoading && 'animate-spin')} />
            <span>{explanation ? 'Regenerate' : 'Try again'}</span>
          </Button>
        )}
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="space-y-4" role="status" aria-live="polite">
            {[1, 2, 3, 4].map((i) => (
              <motion.div
                key={i}
                className="h-8 bg-theme-bg-accent rounded-organic-sm animate-pulse"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: i * 0.15 }}
              />
            ))}
          </div>
        ) : error ? (
          <div className="space-y-3" role="alert">
            <p className="text-sm text-theme-text-secondary">{error}</p>
            {error.toLowerCase().includes('not configured') && (
              <p className="text-xs text-theme-text-muted">
                Add a Groq API key to the backend environment to enable AI climate analysis.
              </p>
            )}
          </div>
        ) : explanation ? (
          <motion.dl className="space-y-4" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
            {items.map((item, index) => (
              <motion.div
                key={item.label}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.1 + index * 0.1 }}
              >
                <dt className="flex items-center gap-2 text-sm font-medium text-theme-text-secondary mb-1">
                  <span className="text-lg" aria-hidden="true">{item.icon}</span>
                  {item.label}
                </dt>
                <dd className="text-body text-theme-text-primary ml-6 leading-relaxed">
                  {item.content}
                </dd>
              </motion.div>
            ))}
          </motion.dl>
        ) : (
          <p className="text-sm text-theme-text-secondary">
            Generate an AI explanation of this location&apos;s current climate risks and recommended actions.
          </p>
        )}
      </CardContent>
    </Card>
  );
}

interface StreamingTextProps {
  text: string;
  speed?: number;
  className?: string;
}

export function StreamingText({ text, speed = 20, className }: StreamingTextProps) {
  const [displayedText, setDisplayedText] = useState('');
  const [index, setIndex] = useState(0);

  useEffect(() => {
    if (index < text.length) {
      const timeout = setTimeout(() => {
        setDisplayedText(text.slice(0, index + 1));
        setIndex(index + 1);
      }, speed);
      return () => clearTimeout(timeout);
    }
  }, [index, text, speed]);

  useEffect(() => {
    setDisplayedText('');
    setIndex(0);
  }, [text]);

  return <span className={className}>{displayedText}</span>;
}

// Need to add the useState and useEffect imports