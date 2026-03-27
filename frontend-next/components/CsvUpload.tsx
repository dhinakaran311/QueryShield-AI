"use client";

import { useCallback, useState } from "react";
import { Upload, CheckCircle, AlertCircle, FileText, X } from "lucide-react";
import { uploadCsv } from "@/lib/api";

export default function CsvUpload() {
  const [dragging, setDragging] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [tableName, setTableName] = useState("");
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState<{ success: boolean; message: string } | null>(null);

  const pickFile = (f: File | null) => {
    if (!f) return;
    if (!f.name.endsWith(".csv")) {
      setResult({ success: false, message: "Please select a .csv file." });
      return;
    }
    setFile(f);
    setResult(null);
    // Auto-fill table name from filename if empty
    if (!tableName) {
      const name = f.name
        .replace(/\.csv$/i, "")
        .replace(/[^a-z0-9_]/gi, "_")
        .toLowerCase()
        .replace(/_+/g, "_")
        .replace(/^_|_$/g, "");
      setTableName(name || "my_table");
    }
  };

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setDragging(false);
      pickFile(e.dataTransfer.files[0] ?? null);
    },
    [tableName]
  );

  const handleUpload = async () => {
    if (!file || !tableName.trim() || uploading) return;
    setUploading(true);
    setResult(null);
    try {
      const res = await uploadCsv(file, tableName.trim(), "user");
      setResult({ success: true, message: res.data.message });
      setFile(null);
      setTableName("");
    } catch (err: unknown) {
      const detail = (err as { response?: { data?: { detail?: unknown } } })
        ?.response?.data?.detail;
      let msg = "Upload failed. Please try again.";
      if (typeof detail === "string") {
        msg = detail;
      } else if (Array.isArray(detail)) {
        msg = detail.map((d: { msg?: string }) => d.msg).join(", ");
      } else if (detail && typeof detail === "object") {
        msg = JSON.stringify(detail);
      } else if (err instanceof Error) {
        msg = err.message;
      }
      setResult({ success: false, message: msg });
    } finally {
      setUploading(false);
    }
  };

  const canUpload = !!file && !!tableName.trim() && !uploading;

  return (
    <div className="space-y-3">
      {/* ── Drop zone: use a <label> so clicking it natively opens the file picker ── */}
      <label
        htmlFor="csv-file-input"
        onDragEnter={() => setDragging(true)}
        onDragLeave={() => setDragging(false)}
        onDragOver={(e) => e.preventDefault()}
        onDrop={handleDrop}
        className={`flex flex-col items-center justify-center border-2 border-dashed rounded-xl p-5 text-center transition-all cursor-pointer select-none ${
          dragging
            ? "border-violet-400 bg-violet-900/20"
            : "border-slate-600 hover:border-violet-500 hover:bg-violet-900/10 bg-slate-800/30"
        }`}
      >
        {/* Hidden file input — label click natively triggers this */}
        <input
          id="csv-file-input"
          type="file"
          accept=".csv"
          className="sr-only"
          onChange={(e) => pickFile(e.target.files?.[0] ?? null)}
        />

        {file ? (
          <div className="flex items-center justify-between gap-2 w-full">
            <div className="flex items-center gap-2 min-w-0">
              <FileText size={16} className="text-violet-400 shrink-0" />
              <span className="text-sm text-violet-300 font-medium truncate">
                {file.name}
              </span>
              <span className="text-xs text-slate-500 shrink-0">
                ({(file.size / 1024).toFixed(1)} KB)
              </span>
            </div>
            <button
              type="button"
              onClick={(e) => {
                e.preventDefault(); // stop label from opening file picker
                setFile(null);
                setResult(null);
              }}
              className="text-slate-500 hover:text-red-400 transition-colors shrink-0"
            >
              <X size={14} />
            </button>
          </div>
        ) : (
          <>
            <Upload className="mb-2 text-slate-500" size={24} />
            <p className="text-sm text-slate-400">
              Drag & drop or{" "}
              <span className="text-violet-400 underline">click to browse</span>
            </p>
            <p className="text-xs text-slate-600 mt-0.5">CSV files only</p>
          </>
        )}
      </label>

      {/* Table name input */}
      <input
        type="text"
        value={tableName}
        onChange={(e) => setTableName(e.target.value)}
        onKeyDown={(e) => e.key === "Enter" && canUpload && handleUpload()}
        placeholder="Table name (e.g. sales_data)"
        className="w-full bg-slate-800 border border-slate-600 text-slate-200 placeholder-slate-500 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-violet-500 focus:border-transparent transition-colors"
      />

      {/* Upload button */}
      <button
        type="button"
        onClick={handleUpload}
        disabled={!canUpload}
        className={`w-full py-2 rounded-lg text-sm font-semibold transition-all ${
          canUpload
            ? "bg-violet-600 hover:bg-violet-500 text-white shadow-md hover:shadow-violet-500/30 cursor-pointer"
            : "bg-slate-700 text-slate-500 cursor-not-allowed opacity-60"
        }`}
      >
        {uploading ? (
          <span className="flex items-center justify-center gap-2">
            <span className="w-3 h-3 border-2 border-white border-t-transparent rounded-full animate-spin" />
            Uploading…
          </span>
        ) : (
          "🚀 Upload & Create Table"
        )}
      </button>

      {/* Result feedback */}
      {result && (
        <div
          className={`flex items-start gap-2 p-3 rounded-lg text-xs border ${
            result.success
              ? "bg-emerald-900/30 text-emerald-400 border-emerald-700"
              : "bg-red-900/30 text-red-400 border-red-700"
          }`}
        >
          {result.success ? (
            <CheckCircle size={13} className="mt-0.5 shrink-0" />
          ) : (
            <AlertCircle size={13} className="mt-0.5 shrink-0" />
          )}
          <span>{result.message}</span>
        </div>
      )}
    </div>
  );
}
