import { useMemo } from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';

interface SimpleChartProps {
  /** Array of data objects. Auto-detects numeric columns for Y axis. */
  data: Array<Record<string, unknown>>;
  /** Optional chart title. */
  title?: string;
}

/** Color palette for multiple numeric columns. */
const BAR_COLORS = ['#3b82f6', '#10b981', '#8b5cf6', '#f59e0b', '#ef4444', '#06b6d4'];

/**
 * Simple bar chart that auto-detects column types.
 *
 * Uses the first string column as the X axis category and renders
 * a bar for each numeric column detected in the data.
 */
export function SimpleChart({ data, title }: SimpleChartProps) {
  const { xKey, numericKeys } = useMemo(() => {
    if (data.length === 0) return { xKey: '', numericKeys: [] };

    const keys = Object.keys(data[0]);
    let firstStringKey = '';
    const numKeys: string[] = [];

    for (const key of keys) {
      // Sample a few rows to determine type
      const sample = data.slice(0, 5).map(row => row[key]);
      const isNumeric = sample.every(v => typeof v === 'number' || (typeof v === 'string' && !isNaN(Number(v)) && v.trim() !== ''));

      if (isNumeric) {
        numKeys.push(key);
      } else if (!firstStringKey) {
        firstStringKey = key;
      }
    }

    // Fallback: use the first key as X if no string column found
    if (!firstStringKey && keys.length > 0) {
      firstStringKey = keys[0];
    }

    return { xKey: firstStringKey, numericKeys: numKeys };
  }, [data]);

  if (data.length === 0 || numericKeys.length === 0) {
    return (
      <p className="text-sm text-gray-500 italic">
        No numeric data available for charting.
      </p>
    );
  }

  // Convert string numbers to actual numbers for recharts
  const chartData = data.map(row => {
    const converted: Record<string, unknown> = { ...row };
    for (const key of numericKeys) {
      const val = row[key];
      converted[key] = typeof val === 'number' ? val : Number(val);
    }
    return converted;
  });

  return (
    <div className="border border-gray-200 rounded-lg p-4 bg-white">
      {title && (
        <h3 className="text-sm font-medium text-gray-700 mb-3">{title}</h3>
      )}
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={chartData} margin={{ top: 5, right: 20, left: 10, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis
            dataKey={xKey}
            tick={{ fontSize: 12, fill: '#6b7280' }}
            tickLine={false}
            axisLine={{ stroke: '#d1d5db' }}
          />
          <YAxis
            tick={{ fontSize: 12, fill: '#6b7280' }}
            tickLine={false}
            axisLine={{ stroke: '#d1d5db' }}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: '#fff',
              border: '1px solid #e5e7eb',
              borderRadius: '0.5rem',
              fontSize: '0.875rem',
            }}
          />
          {numericKeys.length > 1 && <Legend />}
          {numericKeys.map((key, i) => (
            <Bar
              key={key}
              dataKey={key}
              fill={BAR_COLORS[i % BAR_COLORS.length]}
              radius={[4, 4, 0, 0]}
            />
          ))}
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
