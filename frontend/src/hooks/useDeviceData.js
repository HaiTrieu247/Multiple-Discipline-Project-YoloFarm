import { useEffect, useState } from 'react';
import { getStatus } from '../services/api';

export function useDeviceData() {
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let mounted = true;

    const refreshStatus = async () => {
      try {
        const data = await getStatus();
        if (!mounted) return;
        setStatus(data);
        setLoading(false);
        setError(null);
      } catch (err) {
        if (!mounted) return;
        setError(err);
        setLoading(false);
      }
    };

    refreshStatus();
    const interval = window.setInterval(refreshStatus, 1000);
    return () => {
      mounted = false;
      window.clearInterval(interval);
    };
  }, []);

  return {
    status,
    loading,
    error,
    refetch: async () => {
      try {
        const data = await getStatus();
        setStatus(data);
        setError(null);
      } catch (err) {
        setError(err);
      }
    },
  };
}
