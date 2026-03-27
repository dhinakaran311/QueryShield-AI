"use client";

interface RoleSelectorProps {
  role: string;
  onChange: (role: string) => void;
}

const ROLES = [
  { value: "Admin",   label: "Admin",   dot: "bg-emerald-500", desc: "Full access" },
  { value: "Analyst", label: "Analyst", dot: "bg-amber-500",   desc: "No HR/salary" },
  { value: "Viewer",  label: "Viewer",  dot: "bg-red-500",     desc: "Public only" },
];

export default function RoleSelector({ role, onChange }: RoleSelectorProps) {
  const current = ROLES.find((r) => r.value === role) ?? ROLES[0];
  return (
    <div className="space-y-2">
      <label className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
        Access Role
      </label>
      <select
        value={role}
        onChange={(e) => onChange(e.target.value)}
        className="w-full bg-slate-800 border border-slate-700 text-slate-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-violet-500 focus:border-transparent transition-colors"
      >
        {ROLES.map((r) => (
          <option key={r.value} value={r.value}>
            {r.label} — {r.desc}
          </option>
        ))}
      </select>
      <div className="flex items-center gap-2 text-xs text-slate-500">
        <span className={`w-2 h-2 rounded-full ${current.dot}`} />
        Active: <span className="font-semibold text-slate-300">{current.label}</span>
      </div>
    </div>
  );
}
