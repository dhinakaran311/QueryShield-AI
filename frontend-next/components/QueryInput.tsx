"use client";

import { useState } from "react";
import { Search, Trash2 } from "lucide-react";

interface QueryInputProps {
  onSubmit: (question: string) => void;
  onClear: () => void;
  loading: boolean;
}

export default function QueryInput({ onSubmit, onClear, loading }: QueryInputProps) {
  const [question, setQuestion] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (question.trim()) onSubmit(question.trim());
  };

  return (
    <form onSubmit={handleSubmit} className="flex gap-2">
      <input
        type="text"
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        placeholder="Ask your data anything… e.g. Show total revenue by category"
        disabled={loading}
        className="flex-1 bg-slate-800 border border-slate-700 text-white placeholder-slate-500 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-violet-500 disabled:opacity-50"
      />
      <button
        type="submit"
        disabled={loading || !question.trim()}
        className="flex items-center gap-2 bg-violet-600 hover:bg-violet-700 disabled:opacity-50 disabled:cursor-not-allowed text-white px-5 py-3 rounded-xl text-sm font-semibold transition-colors"
      >
        <Search size={16} />
        {loading ? "Thinking…" : "Ask AI"}
      </button>
      <button
        type="button"
        onClick={onClear}
        title="Clear history"
        className="p-3 bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-400 hover:text-white rounded-xl transition-colors"
      >
        <Trash2 size={16} />
      </button>
    </form>
  );
}
