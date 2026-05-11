import { useEffect, useState } from 'react';
import { getHistory } from '../services/api';

export function useHistoryData() {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let mounted = true;

    const fetchHistory = async () => {
      try {
        const data = await getHistory({ limit: 100, offset: 0 });
        if (!mounted) return;
        setHistory(data.records || []);
        setLoading(false);
        setError(null);
      } catch (err) {
        if (!mounted) return;
        setError(err);
        setLoading(false);
      }
    };

    fetchHistory();
    const interval = window.setInterval(fetchHistory, 30000);
    return () => {
      mounted = false;
      window.clearInterval(interval);
    };
  }, []);

  return {
    history,
    loading,
    error,
    refetch: async () => {
      setLoading(true);
      try {
        const data = await getHistory({ limit: 100, offset: 0 });
        setHistory(data.records || []);
        setError(null);
      } catch (err) {
        setError(err);
      } finally {
        setLoading(false);
      }
    },
  };
}
