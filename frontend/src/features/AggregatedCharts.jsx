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

const LABELS = {
  daily: { title: 'Theo ngày (30 ngày gần nhất)', subtitle: 'Trung bình mỗi ngày' },
  weekly: { title: 'Theo tuần (12 tuần gần nhất)', subtitle: 'Trung bình mỗi tuần' },
};

export default function AggregatedCharts({ data, loading, error, granularity }) {
  const { title, subtitle } = LABELS[granularity] ?? LABELS.daily;

  return (
    <div className="space-y-6">
      <div className="rounded-3xl bg-white/90 p-6 shadow-[0_20px_45px_rgba(15,23,42,0.18)]">
        <h2 className="text-xl font-semibold text-slate-900 mb-1">📅 {title}</h2>
        <p className="text-sm text-slate-500">{subtitle} — từ /api/history/{granularity}</p>
      </div>

      {loading && (
        <div className="rounded-3xl bg-white p-6 text-slate-600 shadow-[0_20px_45px_rgba(15,23,42,0.18)]">
          Đang tải dữ liệu…
        </div>
      )}

      {error && (
        <div className="rounded-3xl bg-rose-50 p-6 text-rose-700 shadow-[0_20px_45px_rgba(15,23,42,0.18)]">
          Không thể tải dữ liệu. Vui lòng thử lại.
        </div>
      )}

      {!loading && !error && data.length === 0 && (
        <div className="rounded-3xl bg-white p-6 text-slate-500 shadow-[0_20px_45px_rgba(15,23,42,0.18)]">
          Chưa có dữ liệu. Board cần gửi ít nhất một bản ghi trước.
        </div>
      )}

      {!loading && !error && data.length > 0 && (
        <div className="grid gap-6 xl:grid-cols-2">
          {/* Nhiệt độ & Độ ẩm */}
          <div className="rounded-3xl bg-white p-5 shadow-[0_20px_45px_rgba(15,23,42,0.18)]">
            <h3 className="text-lg font-semibold text-slate-900 mb-1">Nhiệt độ & Độ ẩm (trung bình)</h3>
            <p className="text-xs text-slate-400 mb-4">{data.length} khoảng thời gian</p>
            <div className="h-[300px]">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={data} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                  <XAxis dataKey="period" tick={{ fill: '#64748b', fontSize: 11 }} />
                  <YAxis yAxisId="left" orientation="left" tick={{ fill: '#64748b', fontSize: 11 }} />
                  <YAxis yAxisId="right" orientation="right" tick={{ fill: '#64748b', fontSize: 11 }} />
                  <Tooltip
                    labelStyle={{ color: '#0f172a', fontWeight: 600 }}
                    formatter={(v, name) => [v != null ? v.toFixed(1) : '--', name]}
                  />
                  <Line
                    type="monotone"
                    dataKey="temperature_avg"
                    name="Nhiệt độ (°C)"
                    stroke="#667eea"
                    yAxisId="left"
                    strokeWidth={3}
                    dot={{ r: 3 }}
                    activeDot={{ r: 5 }}
                  />
                  <Line
                    type="monotone"
                    dataKey="humidity_avg"
                    name="Độ ẩm (%)"
                    stroke="#22c55e"
                    yAxisId="right"
                    strokeWidth={3}
                    dot={{ r: 3 }}
                    activeDot={{ r: 5 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Độ ẩm đất & Ánh sáng */}
          <div className="rounded-3xl bg-white p-5 shadow-[0_20px_45px_rgba(15,23,42,0.18)]">
            <h3 className="text-lg font-semibold text-slate-900 mb-1">Độ ẩm đất & Ánh sáng (trung bình)</h3>
            <p className="text-xs text-slate-400 mb-4">{data.length} khoảng thời gian</p>
            <div className="h-[300px]">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={data} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
                  <defs>
                    <linearGradient id={`soil-${granularity}`} x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#667eea" stopOpacity={0.8} />
                      <stop offset="95%" stopColor="#667eea" stopOpacity={0.1} />
                    </linearGradient>
                    <linearGradient id={`light-${granularity}`} x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#f97316" stopOpacity={0.8} />
                      <stop offset="95%" stopColor="#f97316" stopOpacity={0.1} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                  <XAxis dataKey="period" tick={{ fill: '#64748b', fontSize: 11 }} />
                  <YAxis tick={{ fill: '#64748b', fontSize: 11 }} />
                  <Tooltip
                    labelStyle={{ color: '#0f172a', fontWeight: 600 }}
                    formatter={(v, name) => [v != null ? v.toFixed(1) : '--', name]}
                  />
                  <Area
                    type="monotone"
                    dataKey="soil_moisture_avg"
                    name="Độ ẩm đất (%)"
                    stroke="#667eea"
                    fill={`url(#soil-${granularity})`}
                  />
                  <Area
                    type="monotone"
                    dataKey="light_level_avg"
                    name="Ánh sáng (lux)"
                    stroke="#f97316"
                    fill={`url(#light-${granularity})`}
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Bảng tóm tắt */}
          <div className="xl:col-span-2 rounded-3xl bg-white p-5 shadow-[0_20px_45px_rgba(15,23,42,0.18)] overflow-x-auto">
            <h3 className="text-lg font-semibold text-slate-900 mb-4">Bảng số liệu</h3>
            <table className="w-full text-sm text-left">
              <thead>
                <tr className="border-b border-slate-200 text-slate-500">
                  <th className="pb-3 pr-4 font-medium">Kỳ</th>
                  <th className="pb-3 pr-4 font-medium">Nhiệt độ (°C)</th>
                  <th className="pb-3 pr-4 font-medium">Độ ẩm (%)</th>
                  <th className="pb-3 pr-4 font-medium">Ẩm đất (%)</th>
                  <th className="pb-3 pr-4 font-medium">Ánh sáng</th>
                  <th className="pb-3 font-medium">Số đo</th>
                </tr>
              </thead>
              <tbody>
                {[...data].reverse().map((row) => (
                  <tr key={row.period} className="border-b border-slate-100 hover:bg-slate-50">
                    <td className="py-2 pr-4 font-mono text-slate-700">{row.period}</td>
                    <td className="py-2 pr-4 text-[#667eea] font-semibold">
                      {row.temperature_avg != null ? row.temperature_avg.toFixed(1) : '--'}
                    </td>
                    <td className="py-2 pr-4 text-green-600 font-semibold">
                      {row.humidity_avg != null ? row.humidity_avg.toFixed(1) : '--'}
                    </td>
                    <td className="py-2 pr-4 text-slate-700">
                      {row.soil_moisture_avg != null ? row.soil_moisture_avg.toFixed(1) : '--'}
                    </td>
                    <td className="py-2 pr-4 text-orange-500">
                      {row.light_level_avg != null ? row.light_level_avg.toFixed(0) : '--'}
                    </td>
                    <td className="py-2 text-slate-400">{row.record_count}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
