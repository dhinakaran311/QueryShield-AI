"use client";

interface RoleSelectorProps {
  role: string;
  onChange: (role: string) => void;
}

const ROLES = [
  { value: "Admin", label: "Admin", color: "bg-green-500", desc: "Full access" },
  { value: "Analyst", label: "Analyst", color: "bg-yellow-500", desc: "No HR/salary" },
  { value: "Viewer", label: "Viewer", color: "bg-red-500", desc: "Public only" },
];

export default function RoleSelector({ role, onChange }: RoleSelectorProps) {
  const current = ROLES.find((r) => r.value === role) ?? ROLES[0];

  return (
    <div className="space-y-2">
      <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
        Access Role
      </label>
      <select
        value={role}
        onChange={(e) => onChange(e.target.value)}
        className="w-full bg-slate-800 border border-slate-700 text-white rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-violet-500"
      >
        {ROLES.map((r) => (
          <option key={r.value} value={r.value}>
            {r.label} — {r.desc}
          </option>
        ))}
      </select>
      <div className="flex items-center gap-2 text-xs text-slate-400">
        <span className={`w-2 h-2 rounded-full ${current.color}`} />
        Active: <span className="font-medium text-white">{current.label}</span>
      </div>
    </div>
  );
}
