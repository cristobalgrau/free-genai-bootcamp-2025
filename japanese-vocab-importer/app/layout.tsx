import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'Japanese Vocabulary Importer',
  description: 'Generate Japanese vocabulary lists based on themes',
};

// Add this to suppress hydration warnings in development
const suppressHydrationWarning = process.env.NODE_ENV === 'development';

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning={suppressHydrationWarning}>
      <body className={inter.className}>{children}</body>
    </html>
  );
}