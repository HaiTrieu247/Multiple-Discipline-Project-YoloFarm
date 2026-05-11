import { useEffect, useMemo, useState } from 'react';
import { NavLink, Route, Routes } from 'react-router-dom';
import { Toaster, toast } from 'react-hot-toast';
import RealtimeDashboard from './features/RealtimeDashboard';
import PumpControls from './features/PumpControls';
import HistoryCharts from './features/HistoryCharts';
import AggregatedCharts from './features/AggregatedCharts';
import { useDeviceData } from './hooks/useDeviceData';
import { useHistoryData } from './hooks/useHistoryData';
import { useAggregatedData } from './hooks/useAggregatedData';
import { sendCommand } from './services/api';

const tabs = [
  { path: '/', label: 'Thời gian thực' },
  { path: '/history', label: 'Lịch sử' },
  { path: '/daily', label: 'Theo ngày' },
  { path: '/weekly', label: 'Theo tuần' },
];

export default function App() {
  const { status, loading, error, refetch } = useDeviceData();
  const { history, loading: historyLoading, error: historyError, refetch: refetchHistory } = useHistoryData();
  const { data: dailyData, loading: dailyLoading, error: dailyError } = useAggregatedData('daily');
  const { data: weeklyData, loading: weeklyLoading, error: weeklyError } = useAggregatedData('weekly');

  // Optimistic overrides: applied immediately when a command is sent,
  // cleared automatically once the real status from the board catches up.
  const [optimistic, setOptimistic] = useState({});

  const handleCommand = async (command, params) => {
    // Apply optimistic update so UI responds instantly
    const patch = {};
    if (command === 'set_pump_state') patch.pump_state = params.state;
    if (command === 'set_pump_mode') patch.pump_mode = params.mode;
    if (command === 'set_humidity_threshold') patch.humidity_threshold = params.threshold;
    if (Object.keys(patch).length) setOptimistic(o => ({ ...o, ...patch }));

    try {
      await sendCommand(command, params);
      toast.success('Gửi lệnh thành công');
    } catch (err) {
      setOptimistic({});          // revert on failure
      toast.error('Gửi lệnh thất bại');
    }
  };

  const statusCard = useMemo(() => {
    const base = {
      temperature: status?.temperature ?? null,
      humidity: status?.humidity ?? null,
      soil_moisture: status?.soil_moisture ?? null,
      light_level: status?.light_level ?? null,
      pump_state: status?.pump_state ?? 0,
      pump_mode: status?.pump_mode ?? 'manual',
      humidity_threshold: status?.humidity_threshold ?? 50,
      timestamp: status?.timestamp ?? null,
    };
    // Merge optimistic overrides; clear them once real status matches
    const merged = { ...base, ...optimistic };
    const allMatch = Object.entries(optimistic).every(([k, v]) => base[k] === v);
    if (allMatch && Object.keys(optimistic).length) setOptimistic({});
    return merged;
  }, [status, optimistic]);

  return (
    <div className="min-h-screen px-4 py-6 sm:px-6 lg:px-8">
      <Toaster position="top-right" />
      <div className="mx-auto max-w-7xl">
        <div className="mb-6 flex flex-col gap-4 rounded-3xl bg-white/10 p-5 shadow-lg backdrop-blur-xl text-white sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="text-3xl font-semibold">🚰 Yolobit Dashboard</h1>
            <p className="mt-2 text-slate-200">Giữ nguyên giao diện hiện tại, nhưng giờ dùng React + Tailwind.</p>
          </div>
          <div className="flex flex-wrap gap-2">
            {tabs.map((tab) => (
              <NavLink
                key={tab.path}
                to={tab.path}
                end={tab.path === '/'}
                className={({ isActive }) =>
                  `rounded-2xl px-4 py-2 text-sm font-semibold transition ${
                    isActive ? 'bg-white text-slate-900 shadow-lg' : 'bg-white/10 text-white hover:bg-white/20'
                  }`
                }
              >
                {tab.label}
              </NavLink>
            ))}
          </div>
        </div>

        <Routes>
          <Route
            path="/"
            element={
              <div className="space-y-6">
                <RealtimeDashboard status={statusCard} loading={loading} error={error} />
                <PumpControls status={statusCard} onSendCommand={handleCommand} />
              </div>
            }
          />
          <Route path="/history" element={<HistoryCharts history={history} loading={historyLoading} error={historyError} />} />
          <Route path="/daily" element={<AggregatedCharts data={dailyData} loading={dailyLoading} error={dailyError} granularity="daily" />} />
          <Route path="/weekly" element={<AggregatedCharts data={weeklyData} loading={weeklyLoading} error={weeklyError} granularity="weekly" />} />
        </Routes>
      </div>
    </div>
  );
}
