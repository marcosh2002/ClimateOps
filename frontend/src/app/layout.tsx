import type { Metadata, Viewport } from 'next';
import { Inter, Fraunces, DM_Sans, JetBrains_Mono } from 'next/font/google';
import '../styles/globals.css';
import { ThemeProvider } from '@/components/providers/ThemeProvider';
import { Toaster } from 'sonner';

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-inter',
  display: 'swap',
});

const fraunces = Fraunces({
  subsets: ['latin'],
  variable: '--font-fraunces',
  display: 'swap',
  weight: ['400', '500', '600', '700', '800', '900'],
});

const dmSans = DM_Sans({
  subsets: ['latin'],
  variable: '--font-dm-sans',
  display: 'swap',
  weight: ['400', '500', '600', '700'],
});

const jetbrainsMono = JetBrains_Mono({
  subsets: ['latin'],
  variable: '--font-jetbrains-mono',
  display: 'swap',
});

export const metadata: Metadata = {
  title: 'ClimateOps — Climate Intelligence & Emergency Response',
  description: 'AI-powered platform for global climate risk analysis and live emergency monitoring for India.',
  keywords: ['climate', 'risk', 'heat', 'flood', 'drought', 'water stress', 'emergency', 'monitoring', 'India'],
  authors: [{ name: 'ClimateOps Team' }],
  creator: 'ClimateOps',
  publisher: 'ClimateOps',
  formatDetection: { telephone: false },
  metadataBase: new URL('https://climatify.app'),
  openGraph: {
    type: 'website',
    locale: 'en_US',
    url: 'https://climatify.app',
    title: 'ClimateOps — Climate Intelligence & Emergency Response',
    description: 'Turn climate data into decisions. Global risk analysis, what-if simulations, and live emergency monitoring for India.',
    siteName: 'ClimateOps',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'ClimateOps — Climate Intelligence & Emergency Response',
    description: 'Turn climate data into decisions.',
  },
  robots: { index: true, follow: true },
};

export const viewport: Viewport = {
  themeColor: [
    { media: '(prefers-color-scheme: light)', color: '#fefefe' },
    { media: '(prefers-color-scheme: dark)', color: '#121812' },
  ],
  width: 'device-width',
  initialScale: 1,
  maximumScale: 5,
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const fontVariables = `${inter.variable} ${fraunces.variable} ${dmSans.variable} ${jetbrainsMono.variable}`;

  return (
    <html lang="en" className={fontVariables} suppressHydrationWarning>
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link rel="preconnect" href="https://tile.openstreetmap.org" />
        <link rel="preconnect" href="https://server.arcgisonline.com" />
      </head>
      <body className="min-h-screen bg-theme-bg-primary text-theme-text-primary antialiased">
        <ThemeProvider>
          {children}
          <Toaster
            position="bottom-right"
            theme="system"
            className="bg-theme-bg-secondary border border-theme-border"
            toastOptions={{
              className: 'bg-theme-bg-secondary border border-theme-border',
              style: { background: 'var(--theme-bg-secondary)', border: '1px solid var(--theme-border)' },
              classNames: {
                success: 'bg-forest-100 text-forest-900 border border-forest-200',
                error: 'bg-red-100 text-red-900 border border-red-200',
              },
            }}
          />
        </ThemeProvider>
      </body>
    </html>
  );
}