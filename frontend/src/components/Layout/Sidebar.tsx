import { SourcePanel } from '../DataSources/SourcePanel';
import { ConnectionForm } from '../DataSources/ConnectionForm';
import type { DataSource } from '../../types';

interface SidebarProps {
  sources: DataSource[];
  loading: boolean;
  onRefresh: () => void;
}

/**
 * Left sidebar showing connected data sources and the connection form.
 */
export function Sidebar({ sources, loading, onRefresh }: SidebarProps) {
  return (
    <aside className="w-64 bg-gray-900 border-r border-gray-800 flex flex-col shrink-0 overflow-y-auto">
      <div className="p-4 border-b border-gray-800">
        <h2 className="text-sm font-semibold text-gray-300 uppercase tracking-wide">
          Data Sources
        </h2>
      </div>

      <div className="flex-1 p-4 space-y-4">
        <SourcePanel sources={sources} loading={loading} onRefresh={onRefresh} />
      </div>

      <div className="p-4 border-t border-gray-800">
        <ConnectionForm />
      </div>
    </aside>
  );
}
