"use client";

import {
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

interface ChartViewProps {
  data: Record<string, unknown>[];
  columns: string[];
}

export default function ChartView({ data, columns }: ChartViewProps) {
  if (!data.length || !columns.length) return null;

  const numericCols = columns.filter((c) =>
    data.every((r) => !isNaN(Number(r[c])))
  );
  const categoricalCols = columns.filter((c) => !numericCols.includes(c));

  // Single-value KPI
  if (data.length === 1 && numericCols.length === 1 && columns.length === 1) {
    return (
      <div className="rounded-xl bg-gradient-to-br from-violet-600 to-indigo-700 p-6 text-center">
        <p className="text-sm text-violet-200 mb-1">{numericCols[0]}</p>
        <p className="text-4xl font-bold text-white">
          {Number(data[0][numericCols[0]]).toLocaleString()}
        </p>
      </div>
    );
  }

  const catCol = categoricalCols[0];
  const numCol = numericCols[0];

  if (!catCol || !numCol) return null;

  const chartData = data.map((r) => ({
    name: String(r[catCol] ?? ""),
    value: Number(r[numCol] ?? 0),
  }));

  const isTimeSeries =
    catCol.toLowerCase().includes("date") ||
    catCol.toLowerCase().includes("month") ||
    catCol.toLowerCase().includes("year");

  return (
    <div className="rounded-xl border border-slate-700 bg-slate-900 p-4">
      <p className="text-xs text-slate-400 mb-4 font-semibold uppercase tracking-wider">
        {isTimeSeries ? "📈 Trend" : "📊 Comparison"} — {numCol} by {catCol}
      </p>
      <ResponsiveContainer width="100%" height={240}>
        {isTimeSeries ? (
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
            <XAxis dataKey="name" tick={{ fill: "#94a3b8", fontSize: 11 }} />
            <YAxis tick={{ fill: "#94a3b8", fontSize: 11 }} />
            <Tooltip
              contentStyle={{ backgroundColor: "#1e293b", border: "1px solid #334155", borderRadius: "8px" }}
              labelStyle={{ color: "#e2e8f0" }}
            />
            <Line type="monotone" dataKey="value" stroke="#8b5cf6" strokeWidth={2} dot={false} />
          </LineChart>
        ) : (
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
            <XAxis dataKey="name" tick={{ fill: "#94a3b8", fontSize: 11 }} />
            <YAxis tick={{ fill: "#94a3b8", fontSize: 11 }} />
            <Tooltip
              contentStyle={{ backgroundColor: "#1e293b", border: "1px solid #334155", borderRadius: "8px" }}
              labelStyle={{ color: "#e2e8f0" }}
            />
            <Bar dataKey="value" fill="#8b5cf6" radius={[4, 4, 0, 0]} />
          </BarChart>
        )}
      </ResponsiveContainer>
    </div>
  );
}
