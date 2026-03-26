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
    <div className="space-y-4">
      <div
        onDragEnter={() => setDragging(true)}
        onDragLeave={() => setDragging(false)}
        onDragOver={(e) => e.preventDefault()}
        onDrop={handleDrop}
        className={`border-2 border-dashed rounded-xl p-8 text-center transition-colors cursor-pointer ${
          dragging ? "border-violet-500 bg-violet-500/10" : "border-slate-700 hover:border-slate-500"
        }`}
      >
        <Upload className="mx-auto mb-3 text-slate-500" size={32} />
        {file ? (
          <p className="text-sm text-violet-400 font-medium">{file.name}</p>
        ) : (
          <>
            <p className="text-sm text-slate-400">Drag & drop a CSV file here</p>
            <p className="text-xs text-slate-600 mt-1">or</p>
            <label className="mt-2 inline-block text-xs text-violet-400 hover:text-violet-300 cursor-pointer underline">
              browse files
              <input
                type="file"
                accept=".csv"
                className="hidden"
                onChange={(e) => setFile(e.target.files?.[0] ?? null)}
              />
            </label>
          </>
        )}
      </div>

      <input
        type="text"
        value={tableName}
        onChange={(e) => setTableName(e.target.value)}
        placeholder="Table name (e.g. sales_data)"
        className="w-full bg-slate-800 border border-slate-700 text-white placeholder-slate-500 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-violet-500"
      />

      <button
        onClick={handleUpload}
        disabled={!file || !tableName.trim() || uploading}
        className="w-full bg-violet-600 hover:bg-violet-700 disabled:opacity-50 disabled:cursor-not-allowed text-white py-2.5 rounded-lg text-sm font-semibold transition-colors"
      >
        {uploading ? "Uploading…" : "🚀 Upload & Create Table"}
      </button>

      {result && (
        <div
          className={`flex items-start gap-2 p-3 rounded-lg text-sm ${
            result.success ? "bg-green-900/30 text-green-400 border border-green-800" : "bg-red-900/30 text-red-400 border border-red-800"
          }`}
        >
          {result.success ? <CheckCircle size={16} className="mt-0.5 shrink-0" /> : <AlertCircle size={16} className="mt-0.5 shrink-0" />}
          {result.message}
        </div>
      )}
    </div>
  );
}
