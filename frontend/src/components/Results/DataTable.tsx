import { useState, useMemo, useCallback } from 'react';

interface DataTableProps {
  /** Array of row objects. Keys become column headers. */
  rows: Array<Record<string, unknown>>;
  /** Optional max rows to display before truncation. Defaults to 100. */
  maxRows?: number;
}

type SortDirection = 'asc' | 'desc' | null;

interface SortState {
  column: string;
  direction: SortDirection;
}

/**
 * Styled HTML table with alternating row colors and sortable headers.
 *
 * Click a column header to sort ascending, click again for descending,
 * and once more to clear the sort. Keyboard accessible via tab and
 * Enter/Space to toggle sort.
 */
export function DataTable({ rows, maxRows = 100 }: DataTableProps) {
  const [sort, setSort] = useState<SortState>({ column: '', direction: null });

  const columns = useMemo(() => {
    if (rows.length === 0) return [];
    return Object.keys(rows[0]);
  }, [rows]);

  const handleSort = useCallback(
    (column: string) => {
      setSort(prev => {
        if (prev.column !== column) return { column, direction: 'asc' };
        if (prev.direction === 'asc') return { column, direction: 'desc' };
        return { column: '', direction: null };
      });
    },
    []
  );

  const sortedRows = useMemo(() => {
    if (!sort.direction || !sort.column) return rows;
    const col = sort.column;
    const dir = sort.direction === 'asc' ? 1 : -1;

    return [...rows].sort((a, b) => {
      const aVal = a[col];
      const bVal = b[col];
      if (aVal == null && bVal == null) return 0;
      if (aVal == null) return dir;
      if (bVal == null) return -dir;
      if (typeof aVal === 'number' && typeof bVal === 'number') {
        return (aVal - bVal) * dir;
      }
      return String(aVal).localeCompare(String(bVal)) * dir;
    });
  }, [rows, sort]);

  const displayRows = sortedRows.slice(0, maxRows);

  if (rows.length === 0) {
    return <p className="text-sm text-gray-400 italic">No data to display.</p>;
  }

  return (
    <div className="overflow-x-auto border border-gray-700 rounded-lg">
      <table className="min-w-full text-sm">
        <thead>
          <tr className="bg-gray-800 border-b border-gray-700">
            {columns.map(col => {
              const isActive = sort.column === col;
              let indicator = '';
              if (isActive && sort.direction === 'asc') indicator = ' [asc]';
              if (isActive && sort.direction === 'desc') indicator = ' [desc]';

              return (
                <th
                  key={col}
                  className="px-3 py-2 text-left font-medium text-gray-300 cursor-pointer select-none hover:bg-gray-700 transition-colors"
                  onClick={() => handleSort(col)}
                  onKeyDown={e => {
                    if (e.key === 'Enter' || e.key === ' ') {
                      e.preventDefault();
                      handleSort(col);
                    }
                  }}
                  tabIndex={0}
                  role="columnheader"
                  aria-sort={
                    isActive && sort.direction === 'asc'
                      ? 'ascending'
                      : isActive && sort.direction === 'desc'
                        ? 'descending'
                        : 'none'
                  }
                >
                  {col}{indicator}
                </th>
              );
            })}
          </tr>
        </thead>
        <tbody>
          {displayRows.map((row, idx) => (
            <tr
              key={idx}
              className={idx % 2 === 0 ? 'bg-gray-900' : 'bg-gray-800/50'}
            >
              {columns.map(col => (
                <td key={col} className="px-3 py-2 text-gray-200 border-t border-gray-800">
                  {row[col] == null ? '' : String(row[col])}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
      {rows.length > maxRows && (
        <p className="text-xs text-gray-500 px-3 py-2 bg-gray-800 border-t border-gray-700">
          Showing {maxRows} of {rows.length} rows
        </p>
      )}
    </div>
  );
}
