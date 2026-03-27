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
            ? <span className="text-slate-500 font-mono text-xs bg-slate-700 px-1.5 py-0.5 rounded">***</span>
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

  if (!data.length) return (
    <div className="text-center text-slate-500 py-8">No rows returned.</div>
  );

  return (
    <div className="space-y-3">
      <div className="overflow-x-auto rounded-xl border border-slate-700">
        <table className="w-full text-sm">
          <thead>
            {table.getHeaderGroups().map((hg) => (
              <tr key={hg.id} className="border-b border-slate-700 bg-slate-800">
                {hg.headers.map((header) => (
                  <th key={header.id}
                    onClick={header.column.getToggleSortingHandler()}
                    className="px-4 py-3 text-left text-xs font-semibold text-slate-400 uppercase tracking-wider cursor-pointer select-none hover:text-violet-400 transition-colors"
                  >
                    <div className="flex items-center gap-1">
                      {flexRender(header.column.columnDef.header, header.getContext())}
                      {header.column.getIsSorted() === "asc" ? <ChevronUp size={13} /> :
                       header.column.getIsSorted() === "desc" ? <ChevronDown size={13} /> :
                       <ChevronsUpDown size={13} className="text-slate-600" />}
                    </div>
                  </th>
                ))}
              </tr>
            ))}
          </thead>
          <tbody>
            {table.getRowModel().rows.map((row, i) => (
              <tr key={row.id}
                className={`border-b border-slate-800 ${i % 2 === 0 ? "bg-slate-900" : "bg-slate-900/50"} hover:bg-violet-900/20 transition-colors`}
              >
                {row.getVisibleCells().map((cell) => (
                  <td key={cell.id} className="px-4 py-2.5 text-slate-300">
                    {flexRender(cell.column.columnDef.cell, cell.getContext())}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="flex items-center justify-between text-xs text-slate-500">
        <span>
          Showing {table.getState().pagination.pageIndex * 10 + 1}–
          {Math.min((table.getState().pagination.pageIndex + 1) * 10, data.length)} of {data.length} rows
        </span>
        <div className="flex gap-1">
          <button onClick={() => table.previousPage()} disabled={!table.getCanPreviousPage()}
            className="px-3 py-1 bg-slate-800 border border-slate-700 rounded-lg disabled:opacity-40 hover:bg-slate-700 transition-colors text-slate-300">←</button>
          <button onClick={() => table.nextPage()} disabled={!table.getCanNextPage()}
            className="px-3 py-1 bg-slate-800 border border-slate-700 rounded-lg disabled:opacity-40 hover:bg-slate-700 transition-colors text-slate-300">→</button>
        </div>
      </div>
    </div>
  );
}
