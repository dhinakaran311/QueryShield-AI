"use client";

import { useState } from "react";
import Navbar from "@/components/Navbar";
import RoleSelector from "@/components/RoleSelector";
import QueryInput from "@/components/QueryInput";
import SqlDisplay from "@/components/SqlDisplay";
import ResultsTable from "@/components/ResultsTable";
import ChartView from "@/components/ChartView";
import MemorySidebar from "@/components/MemorySidebar";
import CsvUpload from "@/components/CsvUpload";
import { generateSql, executeSql, ExecuteSqlResponse } from "@/lib/api";
import { Wrench, Zap, MessagesSquare, AlertTriangle } from "lucide-react";

export default function HomePage() {
  const [role, setRole] = useState("Admin");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [sql, setSql] = useState<string | null>(null);
  const [isFollowup, setIsFollowup] = useState(false);
  const [execResult, setExecResult] = useState<ExecuteSqlResponse | null>(null);
  const [lastNl, setLastNl] = useState<string | null>(null);
  const [lastSql, setLastSql] = useState<string | null>(null);

  const handleQuery = async (question: string) => {
    setLoading(true);
    setError(null);
    setExecResult(null);

    try {
      // 1. Generate SQL
      const genRes = await generateSql(question, lastNl, lastSql, role);
      const generatedSql = genRes.data.sql;
      setSql(generatedSql);
      setIsFollowup(genRes.data.is_followup);

      // 2. Execute SQL
      const execRes = await executeSql(question, generatedSql, role);
      setExecResult(execRes.data);

      // 3. Update memory
      const finalSql = execRes.data.was_corrected
        ? (execRes.data.corrected_sql ?? generatedSql)
        : generatedSql;
      setLastNl(question);
      setLastSql(finalSql);
    } catch (err: unknown) {
      const detail = (err as { response?: { data?: { detail?: unknown } } })?.response?.data?.detail;
      if (detail && typeof detail === "object" && "reason" in detail) {
        setError(`🛡️ ${(detail as { reason: string }).reason}`);
      } else {
        setError(String(detail ?? "Something went wrong."));
      }
    } finally {
      setLoading(false);
    }
  };

  const handleClear = () => {
    setSql(null);
    setExecResult(null);
    setError(null);
    setLastNl(null);
    setLastSql(null);
    setIsFollowup(false);
  };

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      <Navbar role={role} />

      <div className="max-w-7xl mx-auto px-6 py-8 flex gap-6">
        {/* Sidebar */}
        <aside className="w-64 shrink-0 space-y-6">
          <RoleSelector role={role} onChange={setRole} />
          <div className="border-t border-slate-800" />
          <MemorySidebar lastNl={lastNl} lastSql={lastSql} />
          <div className="border-t border-slate-800" />
          <div className="space-y-2">
            <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Upload CSV</p>
            <CsvUpload />
          </div>
        </aside>

        {/* Main content */}
        <main className="flex-1 min-w-0 space-y-6">
          <div>
            <h1 className="text-2xl font-bold text-white mb-1">Ask your Data</h1>
            <p className="text-sm text-slate-400">
              Ask anything in plain English. QueryShield AI generates, secures, optimizes, and corrects your SQL automatically.
            </p>
          </div>

          <QueryInput onSubmit={handleQuery} onClear={handleClear} loading={loading} />

          {/* Badges */}
          {(isFollowup || execResult?.was_corrected || execResult?.was_optimized) && (
            <div className="flex flex-wrap gap-2">
              {isFollowup && (
                <span className="flex items-center gap-1 text-xs bg-violet-900/40 text-violet-300 border border-violet-800 px-2.5 py-1 rounded-full">
                  <MessagesSquare size={12} /> Smart follow-up detected
                </span>
              )}
              {execResult?.was_corrected && (
                <span className="flex items-center gap-1 text-xs bg-blue-900/40 text-blue-300 border border-blue-800 px-2.5 py-1 rounded-full">
                  <Wrench size={12} /> Auto-corrected
                </span>
              )}
              {execResult?.was_optimized && (
                <span className="flex items-center gap-1 text-xs bg-amber-900/40 text-amber-300 border border-amber-800 px-2.5 py-1 rounded-full">
                  <Zap size={12} /> Auto-optimized
                </span>
              )}
            </div>
          )}

          {/* Error */}
          {error && (
            <div className="flex items-start gap-2 bg-red-900/30 border border-red-800 text-red-400 rounded-xl p-4 text-sm">
              <AlertTriangle size={16} className="mt-0.5 shrink-0" />
              {error}
            </div>
          )}

          {/* SQL */}
          {sql && <SqlDisplay sql={sql} />}
          {execResult?.was_corrected && execResult.corrected_sql && (
            <SqlDisplay sql={execResult.corrected_sql} label="✅ Corrected SQL" />
          )}

          {/* Cost badge */}
          {execResult && (
            <div className="flex items-center gap-3 text-sm">
              <span className="text-slate-400">Query Cost:</span>
              <span className="font-semibold">{execResult.cost_label}</span>
              <span className="text-xs text-slate-600">
                (raw: {execResult.query_cost?.toFixed(1) ?? "N/A"})
              </span>
            </div>
          )}

          {/* Chart + Table */}
          {execResult?.data && execResult.data.length > 0 && (
            <>
              <ChartView data={execResult.data} columns={execResult.columns} />
              <ResultsTable data={execResult.data} columns={execResult.columns} />
            </>
          )}

          {execResult?.message && !execResult.data?.length && (
            <div className="text-slate-500 text-sm text-center py-8">
              {execResult.message}
            </div>
          )}

          {loading && (
            <div className="flex items-center justify-center py-12 text-slate-400 text-sm gap-3">
              <div className="w-5 h-5 border-2 border-violet-500 border-t-transparent rounded-full animate-spin" />
              QueryShield is thinking…
            </div>
          )}
        </main>
      </div>
    </div>
  );
}
