"use client";

import { Brain, Clock } from "lucide-react";

interface MemorySidebarProps {
  lastNl: string | null;
  lastSql: string | null;
}

export default function MemorySidebar({ lastNl, lastSql }: MemorySidebarProps) {
  return (
    <div className="space-y-2">
      <div className="flex items-center gap-2 text-xs font-semibold text-slate-400 uppercase tracking-wider">
        <Brain size={13} />
        Memory Context
      </div>
      {lastNl ? (
        <div className="space-y-2">
          <div className="bg-slate-800 border border-slate-700 rounded-lg p-3 text-xs text-slate-300">
            <div className="flex items-center gap-1 text-slate-500 mb-1">
              <Clock size={11} /> Last question
            </div>
            <p className="text-violet-300">{lastNl}</p>
          </div>
          {lastSql && (
            <details className="text-xs">
              <summary className="text-slate-500 cursor-pointer hover:text-slate-400 transition-colors">
                View SQL memory
              </summary>
              <pre className="mt-2 bg-slate-900 border border-slate-700 rounded-lg p-3 text-green-400 overflow-x-auto whitespace-pre-wrap">
                {lastSql}
              </pre>
            </details>
          )}
        </div>
      ) : (
        <p className="text-xs text-slate-600">No active conversation yet.</p>
      )}
    </div>
  );
}
