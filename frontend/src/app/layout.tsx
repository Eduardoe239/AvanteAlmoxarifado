import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Avante Almoxarifado',
  description: 'Gestão de estoque, patrimônio e empréstimos do laboratório Avante.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="pt-BR">
      <body>{children}</body>
    </html>
  );
}
