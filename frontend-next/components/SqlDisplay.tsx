"use client";

import { Copy, Check } from "lucide-react";
import { useState } from "react";

interface SqlDisplayProps {
  sql: string;
  label?: string;
}

export default function SqlDisplay({ sql, label = "Generated SQL" }: SqlDisplayProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(sql);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="rounded-xl border border-slate-700 overflow-hidden">
      <div className="flex items-center justify-between px-4 py-2 bg-slate-800 border-b border-slate-700">
        <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">{label}</span>
        <button
          onClick={handleCopy}
          className="flex items-center gap-1 text-xs text-slate-500 hover:text-violet-400 transition-colors"
        >
          {copied ? <Check size={13} className="text-emerald-500" /> : <Copy size={13} />}
          {copied ? "Copied!" : "Copy"}
        </button>
      </div>
      <pre className="p-4 text-sm text-violet-300 bg-slate-900 overflow-x-auto whitespace-pre-wrap font-mono">
        {sql}
      </pre>
    </div>
  );
}
