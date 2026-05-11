export default function RealtimeDashboard({ status, loading, error }) {
  const temperature = status?.temperature != null ? `${status.temperature.toFixed(1)}°C` : '--°C';
  const humidity = status?.humidity != null ? `${status.humidity.toFixed(1)}%` : '--%';
  const soilMoisture = status?.soil_moisture != null ? `${status.soil_moisture.toFixed(0)}%` : '--%';
  const lightLevel = status?.light_level != null ? `${status.light_level.toFixed(0)}` : '--';
  const lastUpdate = status?.timestamp
    ? new Date(status.timestamp * 1000).toLocaleTimeString('vi-VN')
    : '--';

  return (
    <div className="space-y-6">
      <div className="rounded-3xl bg-white/10 border border-white/20 p-5 shadow-lg backdrop-blur-xl text-white">
        <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
          <div>
            <h1 className="text-3xl font-semibold">🚰 Yolobit Dashboard</h1>
            <p className="mt-2 text-slate-200">Điều khiển thiết bị từ xa</p>
          </div>
          <div className="flex flex-col gap-2 sm:flex-row sm:items-center">
            <div className="rounded-full bg-white/10 px-4 py-2 text-sm text-white">
              WiFi: {error ? 'Mất kết nối' : 'Kết nối'}
            </div>
            <div className="rounded-full bg-white/10 px-4 py-2 text-sm text-white">
              Cập nhật: {loading ? 'Đang tải...' : lastUpdate}
            </div>
          </div>
        </div>
      </div>

      <div className="grid gap-6 xl:grid-cols-2">
        <div className="rounded-3xl bg-white p-6 shadow-[0_20px_45px_rgba(15,23,42,0.18)]">
          <h2 className="text-xl font-semibold text-slate-900 mb-6">📊 Cảm Biến (DHT20)</h2>
          <div className="grid gap-6 sm:grid-cols-2">
            <div className="rounded-3xl bg-slate-50 p-5 text-center">
              <div className="text-sm text-slate-500">Nhiệt độ</div>
              <div className="text-[2.5rem] font-bold text-[#667eea] mt-4">{temperature}</div>
            </div>
            <div className="rounded-3xl bg-slate-50 p-5 text-center">
              <div className="text-sm text-slate-500">Độ ẩm</div>
              <div className="text-[2.5rem] font-bold text-[#667eea] mt-4">{humidity}</div>
            </div>
          </div>
          <div className="mt-6 rounded-2xl bg-slate-100 p-4 text-sm text-slate-600">
            📍 Đọc từ DHT20 qua I2C
          </div>
        </div>

        <div className="rounded-3xl bg-white p-6 shadow-[0_20px_45px_rgba(15,23,42,0.18)]">
          <h2 className="text-xl font-semibold text-slate-900 mb-6">🌱 Cảm Biến Đất & Ánh Sáng</h2>
          <div className="grid gap-6 sm:grid-cols-2">
            <div className="rounded-3xl bg-slate-50 p-5 text-center">
              <div className="text-sm text-slate-500">Độ ẩm đất</div>
              <div className="text-[2.5rem] font-bold text-[#667eea] mt-4">{soilMoisture}</div>
            </div>
            <div className="rounded-3xl bg-slate-50 p-5 text-center">
              <div className="text-sm text-slate-500">Ánh sáng</div>
              <div className="text-[2.5rem] font-bold text-[#667eea] mt-4">{lightLevel}</div>
            </div>
          </div>
          <div className="mt-6 rounded-2xl bg-slate-100 p-4 text-sm text-slate-600">
            📍 Pin1: Cảm biến độ ẩm đất | Pin2: Cảm biến ánh sáng
          </div>
        </div>
      </div>
    </div>
  );
}
