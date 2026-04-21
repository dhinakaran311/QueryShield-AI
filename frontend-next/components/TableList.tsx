"use client";

import { useCallback, useEffect, useState } from "react";
import { Database, ChevronDown, ChevronRight, RefreshCw, Zap, Table2 } from "lucide-react";
import { getUploadedTables, getTableSchema } from "@/lib/api";

interface TableInfo {
  id: number;
  table_name: string;
  uploaded_by: string;
  upload_time: string;
}

interface ColumnInfo {
  column_name: string;
  data_type: string;
}

interface TableListProps {
  /** Called when user clicks "Query this table" — sets the question in the query input */
  onQueryTable: (question: string) => void;
  /** Increment this to trigger a refresh (e.g. after a successful upload) */
  refreshTrigger?: number;
}

const TYPE_COLOR: Record<string, string> = {
  integer:   "text-blue-400",
  numeric:   "text-cyan-400",
  text:      "text-emerald-400",
  boolean:   "text-amber-400",
  timestamp: "text-violet-400",
  date:      "text-pink-400",
};

function typeColor(dt: string | null | undefined) {
  if (!dt) return "text-slate-400";
  return TYPE_COLOR[dt.toLowerCase()] ?? "text-slate-400";
}

function timeAgo(isoString: string): string {
  const diffMs = Date.now() - new Date(isoString).getTime();
  const mins = Math.floor(diffMs / 60000);
  if (mins < 1)  return "just now";
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24)  return `${hrs}h ago`;
  return `${Math.floor(hrs / 24)}d ago`;
}

export default function TableList({ onQueryTable, refreshTrigger = 0 }: TableListProps) {
  const [tables, setTables]       = useState<TableInfo[]>([]);
  const [loading, setLoading]     = useState(false);
  const [error, setError]         = useState<string | null>(null);
  const [expanded, setExpanded]   = useState<string | null>(null);
  const [schemas, setSchemas]     = useState<Record<string, ColumnInfo[]>>({});
  const [colLoading, setColLoading] = useState<string | null>(null);

  const fetchTables = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await getUploadedTables();
      setTables(res.data.tables);
    } catch {
      setError("Failed to load tables.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchTables(); }, [fetchTables, refreshTrigger]);

  const toggleExpand = async (tableName: string) => {
    if (expanded === tableName) {
      setExpanded(null);
      return;
    }
    setExpanded(tableName);
    if (!schemas[tableName]) {
      setColLoading(tableName);
      try {
        const res = await getTableSchema(tableName);
        setSchemas((prev) => ({ ...prev, [tableName]: res.data.columns }));
      } catch {
        setSchemas((prev) => ({ ...prev, [tableName]: [] }));
      } finally {
        setColLoading(null);
      }
    }
  };

  const handleQuickQuery = (tableName: string, e: React.MouseEvent) => {
    e.stopPropagation();
    onQueryTable(`Show first 20 rows from ${tableName}`);
  };

  return (
    <div className="space-y-2">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2 text-xs font-semibold text-slate-500 uppercase tracking-wider">
          <Database size={13} /> Tables ({tables.length})
        </div>
        <button
          onClick={fetchTables}
          disabled={loading}
          title="Refresh"
          className="text-slate-600 hover:text-violet-400 transition-colors disabled:opacity-40"
        >
          <RefreshCw size={12} className={loading ? "animate-spin" : ""} />
        </button>
      </div>

      {/* Error */}
      {error && <p className="text-xs text-red-400">{error}</p>}

      {/* Empty state */}
      {!loading && tables.length === 0 && !error && (
        <p className="text-xs text-slate-600 italic">
          No tables yet. Upload a CSV to get started.
        </p>
      )}

      {/* Table list */}
      <div className="space-y-1">
        {tables.map((t) => (
          <div key={t.id} className="rounded-lg border border-slate-800 overflow-hidden">
            {/* Table row */}
            <div
              onClick={() => toggleExpand(t.table_name)}
              className="w-full flex items-center gap-2 px-2.5 py-2 text-left hover:bg-slate-800 transition-colors group cursor-pointer"
            >
              {expanded === t.table_name
                ? <ChevronDown size={12} className="text-violet-400 shrink-0" />
                : <ChevronRight size={12} className="text-slate-600 shrink-0" />
              }
              <Table2 size={12} className="text-slate-500 shrink-0" />
              <span className="flex-1 text-xs text-slate-300 font-mono font-medium truncate">
                {t.table_name}
              </span>
              {/* Quick query button */}
              <button
                onClick={(e) => handleQuickQuery(t.table_name, e)}
                title={`Query ${t.table_name}`}
                className="opacity-0 group-hover:opacity-100 transition-opacity text-violet-500 hover:text-violet-300"
              >
                <Zap size={12} />
              </button>
            </div>

            {/* Expanded: columns */}
            {expanded === t.table_name && (
              <div className="border-t border-slate-800 bg-slate-900/60 px-3 py-2 space-y-1">
                {/* Uploaded info */}
                <p className="text-[10px] text-slate-600 mb-2">
                  Uploaded {timeAgo(t.upload_time)} by {t.uploaded_by}
                </p>

                {colLoading === t.table_name ? (
                  <div className="flex items-center gap-1.5 text-xs text-slate-600">
                    <RefreshCw size={10} className="animate-spin" /> Loading columns…
                  </div>
                ) : schemas[t.table_name]?.length ? (
                  <div className="space-y-0.5">
                    {schemas[t.table_name].map((col) => (
                      <div key={col.column_name} className="flex items-center justify-between gap-2">
                        <span className="text-[11px] text-slate-400 font-mono">{col.column_name}</span>
                        <span className={`text-[10px] font-mono ${typeColor(col.data_type)}`}>
                          {col.data_type}
                        </span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-[10px] text-slate-600">No column info.</p>
                )}

                {/* Quick query buttons */}
                <div className="flex flex-col gap-1 pt-2 border-t border-slate-800 mt-2">
                  {[
                    `Show first 20 rows from ${t.table_name}`,
                    `Count all rows in ${t.table_name}`,
                    `Show column summary for ${t.table_name}`,
                  ].map((q) => (
                    <button
                      key={q}
                      onClick={() => onQueryTable(q)}
                      className="text-left text-[10px] text-slate-500 hover:text-violet-400 transition-colors truncate"
                    >
                      ▸ {q}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
