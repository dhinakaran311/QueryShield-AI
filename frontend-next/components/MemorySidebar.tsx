"use client";

import { Brain, Clock } from "lucide-react";

interface MemorySidebarProps {
  lastNl: string | null;
  lastSql: string | null;
}

export default function MemorySidebar({ lastNl, lastSql }: MemorySidebarProps) {
  return (
    <div className="space-y-2">
      <div className="flex items-center gap-2 text-xs font-semibold text-slate-500 uppercase tracking-wider">
        <Brain size={13} /> Memory Context
      </div>
      {lastNl ? (
        <div className="space-y-2">
          <div className="bg-white border border-slate-200 rounded-lg p-3 text-xs shadow-sm">
            <div className="flex items-center gap-1 text-slate-400 mb-1"><Clock size={11} /> Last question</div>
            <p className="text-violet-600 font-medium">{lastNl}</p>
          </div>
          {lastSql && (
            <details className="text-xs">
              <summary className="text-slate-400 cursor-pointer hover:text-violet-600 transition-colors">View SQL memory</summary>
              <pre className="mt-2 bg-violet-50 border border-violet-100 rounded-lg p-3 text-violet-700 overflow-x-auto whitespace-pre-wrap font-mono text-xs">
                {lastSql}
              </pre>
            </details>
          )}
        </div>
      ) : (
        <p className="text-xs text-slate-400">No active conversation yet.</p>
      )}
    </div>
  );
}
