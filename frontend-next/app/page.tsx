"use client";

import { useState } from "react";
import { Shield, Upload, MessageSquare, Search, Trash2, Wrench, Zap, MessagesSquare, AlertTriangle } from "lucide-react";
import RoleSelector from "@/components/RoleSelector";
import SqlDisplay from "@/components/SqlDisplay";
import ResultsTable from "@/components/ResultsTable";
import ChartView from "@/components/ChartView";
import MemorySidebar from "@/components/MemorySidebar";
import CsvUpload from "@/components/CsvUpload";
import TableList from "@/components/TableList";
import { generateSql, executeSql, clearMemory, ExecuteSqlResponse } from "@/lib/api";

type Tab = "query" | "upload";

export default function HomePage() {
  const [tab, setTab] = useState<Tab>("query");
  const [role, setRole] = useState("Admin");
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [sql, setSql] = useState<string | null>(null);
  const [isFollowup, setIsFollowup] = useState(false);
  const [execResult, setExecResult] = useState<ExecuteSqlResponse | null>(null);
  const [lastNl, setLastNl] = useState<string | null>(null);
  const [lastSql, setLastSql] = useState<string | null>(null);
  const [uploadRefresh, setUploadRefresh] = useState(0);

  const handleQuery = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!question.trim()) return;
    setLoading(true);
    setError(null);
    setExecResult(null);
    try {
      const genRes = await generateSql(question.trim(), lastNl, lastSql, role);
      const generatedSql = genRes.data.sql;
      setSql(generatedSql);
      setIsFollowup(genRes.data.is_followup);

      const execRes = await executeSql(question.trim(), generatedSql, role);
      setExecResult(execRes.data);

      const finalSql = execRes.data.was_corrected
        ? (execRes.data.corrected_sql ?? generatedSql)
        : generatedSql;
      setLastNl(question.trim());
      setLastSql(finalSql);
    } catch (err: unknown) {
      const detail = (err as { response?: { data?: { detail?: unknown } } })
        ?.response?.data?.detail;
      if (detail && typeof detail === "object" && "reason" in detail) {
        setError(`🛡️ ${(detail as { reason: string }).reason}`);
        if ((detail as Record<string, unknown>).was_corrected) {
          setExecResult({
            was_corrected: true,
            corrected_sql: (detail as Record<string, unknown>).corrected_sql as string,
            success: false,
            data: [],
            columns: [],
            count: 0,
            query_cost: 0,
            cost_level: "low",
            cost_label: "🟢 Low",
            was_optimized: false,
          });
          setSql((detail as Record<string, unknown>).original_sql as string);
        }
      } else {
        setError(String(detail ?? "Something went wrong. Please try again."));
      }
    } finally {
      setLoading(false);
    }
  };

  const handleClear = async () => {
    try { await clearMemory("default"); } catch { /* silent */ }
    setSql(null); setExecResult(null); setError(null);
    setLastNl(null); setLastSql(null); setIsFollowup(false); setQuestion("");
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      {/* ── Navbar ─────────────────────────────────────────────────────── */}
      <nav className="border-b border-slate-800 bg-slate-950/90 backdrop-blur sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 flex items-center justify-between h-14">
          <div className="flex items-center gap-2 font-bold text-white">
            <div className="w-7 h-7 bg-violet-600 rounded-lg flex items-center justify-center">
              <Shield size={14} className="text-white" />
            </div>
            <span>QueryShield <span className="text-violet-400">AI</span></span>
          </div>

          {/* Tab switcher in navbar */}
          <div className="flex items-center gap-1 bg-slate-900 rounded-xl p-1 border border-slate-800">
            <button
              onClick={() => setTab("query")}
              className={`flex items-center gap-1.5 px-4 py-1.5 rounded-lg text-sm font-medium transition-all ${
                tab === "query"
                  ? "bg-violet-600 text-white shadow"
                  : "text-slate-400 hover:text-white"
              }`}
            >
              <MessageSquare size={14} /> Query
            </button>
            <button
              onClick={() => setTab("upload")}
              className={`flex items-center gap-1.5 px-4 py-1.5 rounded-lg text-sm font-medium transition-all ${
                tab === "upload"
                  ? "bg-violet-600 text-white shadow"
                  : "text-slate-400 hover:text-white"
              }`}
            >
              <Upload size={14} /> Upload CSV
            </button>
          </div>

          {/* Role badge */}
          <span className={`text-xs px-3 py-1 rounded-full border font-semibold ${
            role === "Admin"
              ? "bg-emerald-900/50 text-emerald-400 border-emerald-700"
              : role === "Analyst"
              ? "bg-amber-900/50 text-amber-400 border-amber-700"
              : "bg-red-900/50 text-red-400 border-red-700"
          }`}>
            {role}
          </span>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-6 py-8 flex gap-6">
        {/* ── Sidebar ──────────────────────────────────────────────────── */}
        <aside className="w-60 shrink-0 space-y-4">
          <div className="bg-slate-900 rounded-2xl border border-slate-800 p-4 space-y-4">
            <RoleSelector role={role} onChange={setRole} />
            <div className="border-t border-slate-800" />
            <MemorySidebar lastNl={lastNl} lastSql={lastSql} />
          </div>
          {/* Tables list */}
          <div className="bg-slate-900 rounded-2xl border border-slate-800 p-4">
            <TableList
              refreshTrigger={uploadRefresh}
              onQueryTable={(q) => {
                setQuestion(q);
                setTab("query");
              }}
            />
          </div>
        </aside>

        {/* ── Main content ─────────────────────────────────────────────── */}
        <main className="flex-1 min-w-0 space-y-5">

          {/* ══ QUERY TAB ══ */}
          {tab === "query" && (
            <>
              {/* Query input card */}
              <div className="bg-slate-900 rounded-2xl border border-slate-800 p-6">
                <h1 className="text-xl font-bold mb-1">
                  Ask your <span className="text-violet-400">Data</span>
                </h1>
                <p className="text-sm text-slate-500 mb-5">
                  Plain English → SQL. Secured, optimized, and self-correcting.
                </p>
                <form onSubmit={handleQuery} className="flex gap-2">
                  <input
                    type="text"
                    value={question}
                    onChange={(e) => setQuestion(e.target.value)}
                    placeholder="e.g. Show total revenue by category for 2023"
                    disabled={loading}
                    className="flex-1 bg-slate-800 border border-slate-700 text-slate-100 placeholder-slate-500 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-violet-500 focus:border-transparent transition-colors disabled:opacity-50"
                  />
                  <button
                    type="submit"
                    disabled={loading || !question.trim()}
                    className="flex items-center gap-2 bg-violet-600 hover:bg-violet-500 disabled:opacity-40 disabled:cursor-not-allowed text-white px-5 py-3 rounded-xl text-sm font-semibold transition-colors"
                  >
                    <Search size={16} />
                    {loading ? "Thinking…" : "Ask AI"}
                  </button>
                  <button
                    type="button"
                    onClick={handleClear}
                    title="Clear history"
                    className="p-3 bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-400 hover:text-white rounded-xl transition-colors"
                  >
                    <Trash2 size={16} />
                  </button>
                </form>
              </div>

              {/* Badges */}
              {(isFollowup || execResult?.was_corrected || execResult?.was_optimized) && (
                <div className="flex flex-wrap gap-2">
                  {isFollowup && (
                    <span className="flex items-center gap-1 text-xs bg-violet-900/50 text-violet-400 border border-violet-700 px-2.5 py-1 rounded-full font-medium">
                      <MessagesSquare size={12} /> Smart follow-up detected
                    </span>
                  )}
                  {execResult?.was_corrected && (
                    <span className="flex items-center gap-1 text-xs bg-blue-900/50 text-blue-400 border border-blue-700 px-2.5 py-1 rounded-full font-medium">
                      <Wrench size={12} /> Auto-corrected
                    </span>
                  )}
                  {execResult?.was_optimized && (
                    <span className="flex items-center gap-1 text-xs bg-amber-900/50 text-amber-400 border border-amber-700 px-2.5 py-1 rounded-full font-medium">
                      <Zap size={12} /> Auto-optimized
                    </span>
                  )}
                </div>
              )}

              {/* Error */}
              {error && (
                <div className="flex items-start gap-2 bg-red-900/30 border border-red-700 text-red-400 rounded-xl p-4 text-sm">
                  <AlertTriangle size={16} className="mt-0.5 shrink-0" />
                  {error}
                </div>
              )}

              {/* SQL output */}
              {sql && <SqlDisplay sql={sql} />}
              {execResult?.was_corrected && execResult.corrected_sql && (
                <SqlDisplay sql={execResult.corrected_sql} label="✅ Corrected SQL" />
              )}

              {/* Query cost */}
              {execResult && (
                <div className="flex items-center gap-3 text-sm text-slate-500">
                  <span>Query Cost:</span>
                  <span className="font-semibold text-slate-300">{execResult.cost_label}</span>
                  <span className="text-xs text-slate-600">
                    (raw: {execResult.query_cost?.toFixed(1) ?? "N/A"})
                  </span>
                </div>
              )}

              {/* Loading spinner */}
              {loading && (
                <div className="flex items-center justify-center py-12 text-slate-500 text-sm gap-3">
                  <div className="w-5 h-5 border-2 border-violet-500 border-t-transparent rounded-full animate-spin" />
                  QueryShield is thinking…
                </div>
              )}

              {/* Chart + Table */}
              {execResult?.data && execResult.data.length > 0 && (
                <>
                  <ChartView data={execResult.data} columns={execResult.columns} />
                  <div className="bg-slate-900 rounded-2xl border border-slate-800 p-4">
                    <ResultsTable data={execResult.data} columns={execResult.columns} />
                  </div>
                </>
              )}

              {execResult?.message && !execResult.data?.length && (
                <div className="text-slate-500 text-sm text-center py-8 bg-slate-900 rounded-2xl border border-slate-800">
                  {execResult.message}
                </div>
              )}

              {/* Empty state */}
              {!loading && !sql && !error && (
                <div className="text-center py-16 text-slate-600">
                  <MessageSquare size={40} className="mx-auto mb-3 opacity-30" />
                  <p className="text-sm">Ask a question about your data above.</p>
                  <p className="text-xs mt-1">
                    Don't have data?{" "}
                    <button
                      onClick={() => setTab("upload")}
                      className="text-violet-500 hover:text-violet-400 underline"
                    >
                      Upload a CSV first
                    </button>
                  </p>
                </div>
              )}
            </>
          )}

          {/* ══ UPLOAD TAB ══ */}
          {tab === "upload" && (
            <div className="max-w-xl">
              <div className="bg-slate-900 rounded-2xl border border-slate-800 p-6">
                <h2 className="text-xl font-bold mb-1">Upload CSV Data</h2>
                <p className="text-slate-500 text-sm mb-6">
                  Upload a CSV file to auto-create a queryable table in the database.
                  Then switch to the <strong className="text-slate-300">Query</strong> tab to ask questions about it.
                </p>
                <CsvUpload onSuccess={() => setUploadRefresh((n) => n + 1)} />
              </div>
              <p className="text-xs text-slate-700 mt-3 text-center">
                CSV files up to 50 MB · Table names are auto-sanitized
              </p>
            </div>
          )}

        </main>
      </div>
    </div>
  );
}
