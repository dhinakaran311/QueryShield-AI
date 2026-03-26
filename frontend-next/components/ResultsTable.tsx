"use client";

import {
  useReactTable, getCoreRowModel, getPaginationRowModel,
  getSortedRowModel, flexRender, createColumnHelper, SortingState,
} from "@tanstack/react-table";
import { useState, useMemo } from "react";
import { ChevronUp, ChevronDown, ChevronsUpDown } from "lucide-react";

interface ResultsTableProps {
  data: Record<string, unknown>[];
  columns: string[];
}

export default function ResultsTable({ data, columns }: ResultsTableProps) {
  const [sorting, setSorting] = useState<SortingState>([]);
  const helper = createColumnHelper<Record<string, unknown>>();

  const cols = useMemo(() =>
    columns.map((col) =>
      helper.accessor(col, {
        header: col,
        cell: (info) => {
          const val = info.getValue();
          return val === "***"
            ? <span className="text-slate-400 font-mono text-xs bg-slate-100 px-1.5 py-0.5 rounded">***</span>
            : String(val ?? "");
        },
      })
    ), [columns]);

  const table = useReactTable({
    data, columns: cols, state: { sorting },
    onSortingChange: setSorting,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    initialState: { pagination: { pageSize: 10 } },
  });

  if (!data.length) return <div className="text-center text-slate-400 py-8">No rows returned.</div>;

  return (
    <div className="space-y-3">
      <div className="overflow-x-auto rounded-xl border border-slate-200 shadow-sm">
        <table className="w-full text-sm">
          <thead>
            {table.getHeaderGroups().map((hg) => (
              <tr key={hg.id} className="border-b border-slate-200 bg-slate-50">
                {hg.headers.map((header) => (
                  <th key={header.id} onClick={header.column.getToggleSortingHandler()}
                    className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider cursor-pointer select-none hover:text-violet-600">
                    <div className="flex items-center gap-1">
                      {flexRender(header.column.columnDef.header, header.getContext())}
                      {header.column.getIsSorted() === "asc" ? <ChevronUp size={13} /> :
                       header.column.getIsSorted() === "desc" ? <ChevronDown size={13} /> :
                       <ChevronsUpDown size={13} className="text-slate-300" />}
                    </div>
                  </th>
                ))}
              </tr>
            ))}
          </thead>
          <tbody>
            {table.getRowModel().rows.map((row, i) => (
              <tr key={row.id}
                className={`border-b border-slate-100 ${i % 2 === 0 ? "bg-white" : "bg-slate-50/50"} hover:bg-violet-50 transition-colors`}>
                {row.getVisibleCells().map((cell) => (
                  <td key={cell.id} className="px-4 py-2.5 text-slate-700">
                    {flexRender(cell.column.columnDef.cell, cell.getContext())}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="flex items-center justify-between text-xs text-slate-400">
        <span>
          Showing {table.getState().pagination.pageIndex * 10 + 1}–
          {Math.min((table.getState().pagination.pageIndex + 1) * 10, data.length)} of {data.length} rows
        </span>
        <div className="flex gap-1">
          <button onClick={() => table.previousPage()} disabled={!table.getCanPreviousPage()}
            className="px-3 py-1 bg-white border border-slate-200 rounded-lg disabled:opacity-40 hover:bg-slate-50 transition-colors">←</button>
          <button onClick={() => table.nextPage()} disabled={!table.getCanNextPage()}
            className="px-3 py-1 bg-white border border-slate-200 rounded-lg disabled:opacity-40 hover:bg-slate-50 transition-colors">→</button>
        </div>
      </div>
    </div>
  );
}
