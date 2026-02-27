import { useState, useEffect } from 'react';
import type { DataSource } from '../types';
import { getDataSources } from '../services/api';

/**
 * Hook to fetch and manage connected data sources.
 *
 * Loads the source list from /api/sources on mount and exposes
 * the result along with a refresh function.
 */
export function useDataSources() {
  const [sources, setSources] = useState<DataSource[]>([]);
  const [loading, setLoading] = useState(true);

  const refresh = async () => {
    setLoading(true);
    try {
      const data = await getDataSources();
      setSources(data);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    refresh();
  }, []);

  return { sources, loading, refresh };
}
