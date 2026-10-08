'use client';

import { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { cn } from '@/lib/utils';
import { Search, MapPin, Globe, X } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { api } from '@/lib/api';
import type { SearchResult } from '@/types';

interface SearchAutocompleteProps {
  value: string;
  onChange: (value: string) => void;
  onSearch: (location: SearchResult) => void;
  placeholder?: string;
  className?: string;
  autoFocus?: boolean;
}

export function SearchAutocomplete({
  value,
  onChange,
  onSearch,
  placeholder = 'Search any location on Earth...',
  className,
  autoFocus = false,
}: SearchAutocompleteProps) {
  const [results, setResults] = useState<SearchResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [searchError, setSearchError] = useState<string | null>(null);
  const [isOpen, setIsOpen] = useState(false);
  const [highlightedIndex, setHighlightedIndex] = useState(-1);
  const inputRef = useRef<HTMLInputElement>(null);
  const listRef = useRef<HTMLUListElement>(null);

  useEffect(() => {
    const query = value.trim();
    if (query.length < 2) {
      setResults([]);
      setSearchError(null);
      setIsLoading(false);
      setIsOpen(false);
      return;
    }

    setResults([]);
    setSearchError(null);
    setIsLoading(true);
    setIsOpen(true);
    const controller = new AbortController();
    const timeout = setTimeout(async () => {
      try {
        const data = await api.searchLocations(query, 8, { signal: controller.signal });
        setResults(data);
        setIsOpen(true);
      } catch (error) {
        if (!controller.signal.aborted) {
          setResults([]);
          setSearchError(error instanceof Error ? error.message : 'Unable to search locations.');
          setIsOpen(true);
        }
      } finally {
        if (!controller.signal.aborted) setIsLoading(false);
      }
    }, 300);

    return () => {
      clearTimeout(timeout);
      controller.abort();
    };
  }, [value]);

  useEffect(() => {
    if (isOpen && results.length > 0) {
      setHighlightedIndex(0);
    } else {
      setHighlightedIndex(-1);
    }
  }, [isOpen, results.length]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setHighlightedIndex((prev) => Math.min(prev + 1, results.length - 1));
        break;
      case 'ArrowUp':
        e.preventDefault();
        setHighlightedIndex((prev) => Math.max(prev - 1, 0));
        break;
      case 'Enter':
        e.preventDefault();
        if (highlightedIndex >= 0 && results[highlightedIndex]) {
          onSearch(results[highlightedIndex]);
          onChange('');
          setResults([]);
          setIsOpen(false);
          inputRef.current?.blur();
        }
        break;
      case 'Escape':
        setIsOpen(false);
        inputRef.current?.blur();
        break;
    }
  };

  const handleResultClick = (result: SearchResult) => {
    onSearch(result);
    onChange('');
    setResults([]);
    setIsOpen(false);
    inputRef.current?.blur();
  };

  const handleFocus = () => {
    if (value.trim().length >= 2) setIsOpen(true);
  };

  const handleBlur = () => {
    setTimeout(() => setIsOpen(false), 200);
  };

  const handleClear = () => {
    onChange('');
    setResults([]);
    inputRef.current?.focus();
  };

  return (
    <div className={cn('relative w-full', className)}>
      <div className="relative">
        <label htmlFor="location-search" className="sr-only">
          Search location
        </label>
        <div className="relative">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-theme-text-muted" aria-hidden="true" />
          <input
            ref={inputRef}
            id="location-search"
            type="search"
            value={value}
            onChange={(e) => onChange(e.target.value)}
            onFocus={handleFocus}
            onBlur={handleBlur}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
            autoFocus={autoFocus}
            className={cn(
              'w-full rounded-organic pl-12 pr-12 py-4 text-lg text-theme-text-primary placeholder-theme-text-muted',
              'bg-theme-bg-primary border border-theme-border',
              'focus:border-theme-accent focus:ring-2 focus:ring-theme-accent/20 focus:outline-none',
              'transition-all duration-fast'
            )}
            autoComplete="off"
            aria-autocomplete="list"
            aria-controls="search-results"
            aria-expanded={isOpen && value.trim().length >= 2}
            aria-busy={isLoading}
            role="combobox"
          />
          {value && (
            <Button
              type="button"
              variant="ghost"
              size="sm"
              className="absolute right-3 top-1/2 -translate-y-1/2"
              onClick={handleClear}
              aria-label="Clear search"
            >
              <X className="w-4 h-4" />
            </Button>
          )}
          {isLoading && (
            <div className="absolute right-10 top-1/2 -translate-y-1/2">
              <div className="w-5 h-5 border-2 border-theme-accent border-t-transparent rounded-full animate-spin" aria-hidden="true" />
            </div>
          )}
        </div>
      </div>

      <AnimatePresence>
        {isOpen && value.trim().length >= 2 && (
          <motion.ul
            ref={listRef}
            id="search-results"
            role="listbox"
            className="absolute z-50 top-full left-0 right-0 mt-2 card-organic overflow-hidden shadow-organic-hover"
            initial={{ opacity: 0, y: -10, height: 0 }}
            animate={{ opacity: 1, y: 0, height: 'auto' }}
            exit={{ opacity: 0, y: -10, height: 0 }}
            transition={{ duration: 0.2 }}
          >
            {results.map((result, index) => (
              <motion.li
                key={result.locationId}
                className={cn(
                  'px-4 py-3 cursor-pointer transition-colors',
                  'hover:bg-theme-accent/5',
                  highlightedIndex === index && 'bg-theme-accent/10'
                )}
                onClick={() => handleResultClick(result)}
                onMouseEnter={() => setHighlightedIndex(index)}
                role="option"
                aria-selected={highlightedIndex === index}
                whileHover={{ x: 4 }}
              >
                <div className="flex items-center gap-3">
                  <div className={cn(
                    'w-10 h-10 rounded-organic-sm flex items-center justify-center text-xl',
                    result.source === 'database' ? 'bg-forest-100 dark:bg-forest-900' : 'bg-water-100 dark:bg-water-900'
                  )}>
                    {result.source === 'database' ? <MapPin className="w-5 h-5 text-forest-600 dark:text-forest-400" /> : <Globe className="w-5 h-5 text-water-600 dark:text-water-400" />}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="font-medium text-theme-text-primary truncate">
                      {result.city || result.district || result.state || 'Unnamed location'}
                    </p>
                    <p className="text-sm text-theme-text-muted truncate">
                      {[result.district, result.state, result.country].filter(Boolean).join(', ')}
                    </p>
                  </div>
                  {highlightedIndex === index && (
                    <span className="text-theme-accent" aria-hidden="true">→</span>
                  )}
                </div>
              </motion.li>
            ))}
            {isLoading && (
              <li className="px-4 py-3 text-sm text-theme-text-muted" role="status">
                Searching locations…
              </li>
            )}
            {!isLoading && searchError && (
              <li className="px-4 py-3 text-sm text-risk-critical" role="status">
                Location search failed: {searchError}
              </li>
            )}
            {!isLoading && !searchError && results.length === 0 && (
              <li className="px-4 py-3 text-sm text-theme-text-muted" role="status">
                No matching locations found.
              </li>
            )}
          </motion.ul>
        )}
      </AnimatePresence>
    </div>
  );
}