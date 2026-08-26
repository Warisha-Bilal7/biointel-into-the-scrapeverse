import './globals.css';
import type { Metadata } from 'next';
import { Inter } from 'next/font/google';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'BioIntel Guardian',
  description: 'Biomedical Data Integrity Monitor - Research Dashboard',
  openGraph: {
    images: [
      {
        url: 'https://example.com/og-biointel.png',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    images: [
      {
        url: 'https://example.com/twitter-biointel.png',
      },
    ],
  },
};

import Sidebar from '@/components/sidebar';
import Header from '@/components/header';

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={inter.className} className="min-h-screen bg-background">
        <div className="flex min-h-screen">
          <Sidebar />
          <div className="flex flex-col flex-1 overflow-auto">
            <Header />
            <main className="p-6 md:p-8">
              {children}
            </main>
          </div>
        </div>
      </body>
    </html>
  );
}