import "./globals.css";

export const metadata = {
  title: "Portfolio Optimizer",
  description: "Prophet forecasts + Markowitz optimisation dashboard",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
