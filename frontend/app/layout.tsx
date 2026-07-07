import './globals.css';

export const metadata = {
  title: 'POPclub Copilot',
  description: 'Grounded Assistant',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body suppressHydrationWarning>{children}</body>
    </html>
  );
}