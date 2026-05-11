import { useEffect, useState } from 'react';
import { getDailyHistory, getWeeklyHistory } from '../services/api';

export function useAggregatedData(granularity = 'daily') {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let mounted = true;

    const fetch = async () => {
      try {
        const resp = granularity === 'daily'
          ? await getDailyHistory(30)
          : await getWeeklyHistory(12);
        if (!mounted) return;
        setData(resp.records || []);
        setLoading(false);
        setError(null);
      } catch (err) {
        if (!mounted) return;
        setError(err);
        setLoading(false);
      }
    };

    fetch();
    // Refresh every 5 minutes — aggregated data changes slowly
    const interval = window.setInterval(fetch, 5 * 60 * 1000);
    return () => {
      mounted = false;
      window.clearInterval(interval);
    };
  }, [granularity]);

  return { data, loading, error };
}
