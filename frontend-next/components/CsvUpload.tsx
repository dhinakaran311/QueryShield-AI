"use client";

import { useCallback, useState } from "react";
import { Upload, CheckCircle, AlertCircle } from "lucide-react";
import { uploadCsv } from "@/lib/api";

export default function CsvUpload() {
  const [dragging, setDragging] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [tableName, setTableName] = useState("");
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState<{ success: boolean; message: string } | null>(null);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragging(false);
    const f = e.dataTransfer.files[0];
    if (f?.name.endsWith(".csv")) setFile(f);
  }, []);

  const handleUpload = async () => {
    if (!file || !tableName.trim()) return;
    setUploading(true);
    setResult(null);
    try {
      const res = await uploadCsv(file, tableName.trim(), "user");
      setResult({ success: true, message: res.data.message });
      setFile(null);
      setTableName("");
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ?? "Upload failed";
      setResult({ success: false, message: String(msg) });
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="space-y-3">
      <div
        onDragEnter={() => setDragging(true)}
        onDragLeave={() => setDragging(false)}
        onDragOver={(e) => e.preventDefault()}
        onDrop={handleDrop}
        className={`border-2 border-dashed rounded-xl p-6 text-center transition-colors cursor-pointer ${
          dragging ? "border-violet-400 bg-violet-50" : "border-slate-200 hover:border-violet-300 bg-white"
        }`}
      >
        <Upload className="mx-auto mb-2 text-slate-300" size={28} />
        {file ? (
          <p className="text-sm text-violet-600 font-medium">{file.name}</p>
        ) : (
          <>
            <p className="text-sm text-slate-400">Drag & drop a CSV file</p>
            <label className="mt-1 inline-block text-xs text-violet-500 hover:text-violet-700 cursor-pointer underline">
              browse
              <input type="file" accept=".csv" className="hidden" onChange={(e) => setFile(e.target.files?.[0] ?? null)} />
            </label>
          </>
        )}
      </div>
      <input
        type="text"
        value={tableName}
        onChange={(e) => setTableName(e.target.value)}
        placeholder="Table name (e.g. sales_data)"
        className="w-full bg-white border border-slate-200 text-slate-800 placeholder-slate-400 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-violet-400 shadow-sm"
      />
      <button
        onClick={handleUpload}
        disabled={!file || !tableName.trim() || uploading}
        className="w-full bg-violet-600 hover:bg-violet-700 disabled:opacity-50 disabled:cursor-not-allowed text-white py-2 rounded-lg text-sm font-semibold transition-colors shadow-sm"
      >
        {uploading ? "Uploading…" : "🚀 Upload & Create Table"}
      </button>
      {result && (
        <div className={`flex items-start gap-2 p-3 rounded-lg text-sm border ${
          result.success ? "bg-emerald-50 text-emerald-700 border-emerald-200" : "bg-red-50 text-red-600 border-red-200"
        }`}>
          {result.success ? <CheckCircle size={15} className="mt-0.5 shrink-0" /> : <AlertCircle size={15} className="mt-0.5 shrink-0" />}
          {result.message}
        </div>
      )}
    </div>
  );
}
