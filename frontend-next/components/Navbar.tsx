"use client";

import Link from "next/link";
import { Shield, Upload, MessageSquare } from "lucide-react";

export default function Navbar({ role }: { role: string }) {
  const badge =
    role === "Admin"
      ? "bg-green-500/20 text-green-400 border-green-800"
      : role === "Analyst"
      ? "bg-yellow-500/20 text-yellow-400 border-yellow-800"
      : "bg-red-500/20 text-red-400 border-red-800";

  return (
    <nav className="border-b border-slate-800 bg-slate-950/80 backdrop-blur sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-6 flex items-center justify-between h-14">
        <Link href="/" className="flex items-center gap-2 font-bold text-white">
          <Shield size={20} className="text-violet-400" />
          QueryShield AI
        </Link>

        <div className="flex items-center gap-4">
          <span className={`text-xs px-2.5 py-1 rounded-full border font-medium ${badge}`}>
            {role}
          </span>
          <Link
            href="/"
            className="flex items-center gap-1.5 text-sm text-slate-400 hover:text-white transition-colors"
          >
            <MessageSquare size={15} /> Query
          </Link>
          <Link
            href="/upload"
            className="flex items-center gap-1.5 text-sm text-slate-400 hover:text-white transition-colors"
          >
            <Upload size={15} /> Upload
          </Link>
        </div>
      </div>
    </nav>
  );
}
