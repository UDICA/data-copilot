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

/** Color palette using orange and purple tones. */
const BAR_COLORS = ['#f97316', '#a855f7', '#fb923c', '#c084fc', '#ea580c', '#9333ea'];

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
      <p className="text-sm text-gray-400 italic">
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
    <div className="border border-gray-700 rounded-lg p-4 bg-gray-900">
      {title && (
        <h3 className="text-sm font-medium text-gray-300 mb-3">{title}</h3>
      )}
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={chartData} margin={{ top: 5, right: 20, left: 10, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
          <XAxis
            dataKey={xKey}
            tick={{ fontSize: 12, fill: '#9ca3af' }}
            tickLine={false}
            axisLine={{ stroke: '#4b5563' }}
          />
          <YAxis
            tick={{ fontSize: 12, fill: '#9ca3af' }}
            tickLine={false}
            axisLine={{ stroke: '#4b5563' }}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: '#1f2937',
              border: '1px solid #374151',
              borderRadius: '0.5rem',
              fontSize: '0.875rem',
              color: '#d1d5db',
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
