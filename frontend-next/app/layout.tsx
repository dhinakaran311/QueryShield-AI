import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "QueryShield AI — Secure Text-to-SQL",
  description:
    "Conversational AI that securely converts natural language to SQL with role-based access, cost optimization, and auto-correction.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="antialiased bg-slate-950 text-white">{children}</body>
    </html>
  );
}
