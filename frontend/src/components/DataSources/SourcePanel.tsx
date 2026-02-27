import type { DataSource } from '../../types';

interface SourcePanelProps {
  sources: DataSource[];
  loading: boolean;
  onRefresh: () => void;
}

/** Status dot color mapping. */
const STATUS_COLORS: Record<DataSource['status'], string> = {
  connected: 'bg-green-500',
  disconnected: 'bg-gray-400',
  error: 'bg-red-500',
};

/** Icon for source type. */
function SourceIcon({ type }: { type: DataSource['type'] }) {
  if (type === 'database') {
    return (
      <svg
        xmlns="http://www.w3.org/2000/svg"
        width="16"
        height="16"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
        className="text-gray-500 shrink-0"
        aria-hidden="true"
      >
        <ellipse cx="12" cy="5" rx="9" ry="3" />
        <path d="M3 5V19A9 3 0 0 0 21 19V5" />
        <path d="M3 12A9 3 0 0 0 21 12" />
      </svg>
    );
  }

  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width="16"
      height="16"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      className="text-gray-500 shrink-0"
      aria-hidden="true"
    >
      <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z" />
    </svg>
  );
}

/**
 * Displays the list of data sources with status indicators.
 */
export function SourcePanel({ sources, loading, onRefresh }: SourcePanelProps) {
  if (loading) {
    return (
      <div className="space-y-3">
        {[1, 2].map(i => (
          <div key={i} className="animate-pulse flex items-center gap-2">
            <div className="w-4 h-4 bg-gray-200 rounded" />
            <div className="flex-1">
              <div className="h-3 bg-gray-200 rounded w-24 mb-1" />
              <div className="h-2 bg-gray-200 rounded w-32" />
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (sources.length === 0) {
    return (
      <div className="text-center py-4">
        <p className="text-xs text-gray-500 mb-2">No sources connected</p>
        <button
          type="button"
          onClick={onRefresh}
          className="text-xs text-blue-600 hover:text-blue-700 font-medium focus:outline-none focus:underline"
        >
          Refresh
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-2">
      {sources.map(source => (
        <div
          key={source.id}
          className="flex items-start gap-2 p-2 rounded-md hover:bg-gray-100 transition-colors"
        >
          <SourceIcon type={source.type} />
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-1.5">
              <span className={`w-2 h-2 rounded-full shrink-0 ${STATUS_COLORS[source.status]}`} />
              <span className="text-sm font-medium text-gray-800 truncate">
                {source.name}
              </span>
            </div>
            <p className="text-xs text-gray-500 truncate mt-0.5" title={source.details}>
              {source.details}
            </p>
          </div>
        </div>
      ))}
      <button
        type="button"
        onClick={onRefresh}
        className="w-full text-xs text-gray-500 hover:text-blue-600 py-1.5 font-medium focus:outline-none focus:underline transition-colors"
      >
        Refresh sources
      </button>
    </div>
  );
}
