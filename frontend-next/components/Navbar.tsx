"use client";

import Link from "next/link";
import { Shield, Upload, MessageSquare } from "lucide-react";

export default function Navbar({ role }: { role: string }) {
  const badge =
    role === "Admin"
      ? "bg-emerald-100 text-emerald-700 border-emerald-200"
      : role === "Analyst"
      ? "bg-amber-100 text-amber-700 border-amber-200"
      : "bg-red-100 text-red-700 border-red-200";

  return (
    <nav className="border-b border-slate-200 bg-white/80 backdrop-blur sticky top-0 z-50 shadow-sm">
      <div className="max-w-7xl mx-auto px-6 flex items-center justify-between h-14">
        <Link href="/" className="flex items-center gap-2 font-bold text-slate-800">
          <div className="w-7 h-7 bg-violet-600 rounded-lg flex items-center justify-center">
            <Shield size={14} className="text-white" />
          </div>
          <span>QueryShield <span className="text-violet-600">AI</span></span>
        </Link>

        <div className="flex items-center gap-5">
          <span className={`text-xs px-2.5 py-1 rounded-full border font-semibold ${badge}`}>
            {role}
          </span>
          <Link href="/" className="flex items-center gap-1.5 text-sm text-slate-500 hover:text-violet-600 transition-colors font-medium">
            <MessageSquare size={15} /> Query
          </Link>
          <Link href="/upload" className="flex items-center gap-1.5 text-sm text-slate-500 hover:text-violet-600 transition-colors font-medium">
            <Upload size={15} /> Upload
          </Link>
        </div>
      </div>
    </nav>
  );
}
