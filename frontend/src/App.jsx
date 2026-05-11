import { useMemo } from 'react';
import { NavLink, Route, Routes } from 'react-router-dom';
import { Toaster, toast } from 'react-hot-toast';
import RealtimeDashboard from './features/RealtimeDashboard';
import PumpControls from './features/PumpControls';
import HistoryCharts from './features/HistoryCharts';
import { useDeviceData } from './hooks/useDeviceData';
import { useHistoryData } from './hooks/useHistoryData';
import { sendCommand } from './services/api';

const tabs = [
  { path: '/', label: 'Thời gian thực' },
  { path: '/history', label: 'Lịch sử' },
];

export default function App() {
  const { status, loading, error, refetch } = useDeviceData();
  const { history, loading: historyLoading, error: historyError, refetch: refetchHistory } = useHistoryData();

  const handleCommand = async (command, params) => {
    try {
      await sendCommand(command, params);
      toast.success('Gửi lệnh thành công');
      if (
        command === 'set_pump_state' ||
        command === 'set_pump_mode' ||
        command === 'set_humidity_threshold' ||
        command === 'set_schedule'
      ) {
        refetch();
        refetchHistory();
      }
    } catch (err) {
      toast.error('Gửi lệnh thất bại');
    }
  };

  const statusCard = useMemo(
    () => ({
      temperature: status?.temperature ?? null,
      humidity: status?.humidity ?? null,
      soil_moisture: status?.soil_moisture ?? null,
      light_level: status?.light_level ?? null,
      pump_state: status?.pump_state ?? 0,
      pump_mode: status?.pump_mode ?? 'manual',
      humidity_threshold: status?.humidity_threshold ?? 50,
    }),
    [status]
  );

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
        </Routes>
      </div>
    </div>
  );
}
