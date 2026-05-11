import {
  Area,
  AreaChart,
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';

function formatTimestamp(timestamp) {
  if (!timestamp) return '--';
  return new Date(timestamp * 1000).toLocaleDateString('vi-VN', {
    day: '2-digit',
    month: '2-digit',
  });
}

export default function HistoryCharts({ history, loading, error }) {
  const normalized = [...history]
    .sort((a, b) => a.timestamp - b.timestamp)
    .map((item) => ({
      ...item,
      timeLabel: formatTimestamp(item.timestamp),
    }));

  return (
    <div className="space-y-6">
      <div className="rounded-3xl bg-white/90 p-6 shadow-[0_20px_45px_rgba(15,23,42,0.18)]">
        <h2 className="text-xl font-semibold text-slate-900 mb-2">📈 Lịch sử 30 ngày</h2>
        <p className="text-sm text-slate-500">Dữ liệu cảm biến được lấy từ endpoint /api/history</p>
      </div>

      {loading && (
        <div className="rounded-3xl bg-white p-6 text-slate-600 shadow-[0_20px_45px_rgba(15,23,42,0.18)]">Đang tải dữ liệu lịch sử...</div>
      )}

      {error && (
        <div className="rounded-3xl bg-rose-50 p-6 text-rose-700 shadow-[0_20px_45px_rgba(15,23,42,0.18)]">
          Không thể tải lịch sử. Vui lòng thử lại.
        </div>
      )}

      {!loading && !error && (
        <div className="grid gap-6 xl:grid-cols-2">
          <div className="rounded-3xl bg-white p-5 shadow-[0_20px_45px_rgba(15,23,42,0.18)]">
            <h3 className="text-lg font-semibold text-slate-900 mb-4">Nhiệt độ & Độ ẩm</h3>
            <div className="h-[320px]">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={normalized} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                  <XAxis dataKey="timeLabel" tick={{ fill: '#64748b', fontSize: 12 }} />
                  <YAxis yAxisId="left" orientation="left" tick={{ fill: '#64748b', fontSize: 12 }} />
                  <YAxis yAxisId="right" orientation="right" tick={{ fill: '#64748b', fontSize: 12 }} />
                  <Tooltip labelStyle={{ color: '#0f172a' }} />
                  <Line type="monotone" dataKey="temperature" name="Nhiệt độ" stroke="#667eea" yAxisId="left" strokeWidth={3} dot={false} />
                  <Line type="monotone" dataKey="humidity" name="Độ ẩm" stroke="#22c55e" yAxisId="right" strokeWidth={3} dot={false} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="rounded-3xl bg-white p-5 shadow-[0_20px_45px_rgba(15,23,42,0.18)]">
            <h3 className="text-lg font-semibold text-slate-900 mb-4">Độ ẩm đất & Ánh sáng</h3>
            <div className="h-[320px]">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={normalized} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
                  <defs>
                    <linearGradient id="soilGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#667eea" stopOpacity={0.8} />
                      <stop offset="95%" stopColor="#667eea" stopOpacity={0.1} />
                    </linearGradient>
                    <linearGradient id="lightGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#f97316" stopOpacity={0.8} />
                      <stop offset="95%" stopColor="#f97316" stopOpacity={0.1} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                  <XAxis dataKey="timeLabel" tick={{ fill: '#64748b', fontSize: 12 }} />
                  <YAxis tick={{ fill: '#64748b', fontSize: 12 }} />
                  <Tooltip labelStyle={{ color: '#0f172a' }} />
                  <Area type="monotone" dataKey="soil_moisture" name="Độ ẩm đất" stroke="#667eea" fill="url(#soilGradient)" />
                  <Area type="monotone" dataKey="light_level" name="Ánh sáng" stroke="#f97316" fill="url(#lightGradient)" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
