import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "QueryShield AI — Secure Text-to-SQL",
  description: "Conversational AI that converts natural language to SQL with role-based access, cost optimization, and auto-correction.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className="bg-slate-50 text-slate-900 antialiased" suppressHydrationWarning>
        {children}
      </body>
    </html>
  );
}
