import { useEffect, useMemo, useState } from 'react';
import Button from '../components/ui/Button';

const modeOptions = [
  { value: 'manual', label: 'Manual (Thủ công)' },
  { value: 'auto', label: 'Auto (Theo độ ẩm)' },
  { value: 'scheduled', label: 'Scheduled (Hẹn giờ)' },
];

export default function PumpControls({ status, onSendCommand }) {
  const [mode, setMode] = useState(status?.pump_mode || 'manual');
  const [threshold, setThreshold] = useState(status?.humidity_threshold ?? 50);
  const [schedule, setSchedule] = useState({
    start_hour: 6,
    start_min: 0,
    end_hour: 22,
    end_min: 0,
    duration_sec: 15,
  });

  useEffect(() => {
    if (status) {
      setMode(status.pump_mode || 'manual');
      setThreshold(status.humidity_threshold ?? 50);
    }
  }, [status]);

  const pumpStatus = useMemo(() => {
    if (!status) return { label: 'Đang tải...', color: 'bg-slate-200 text-slate-700' };
    return status.pump_state
      ? { label: 'BẬT', color: 'bg-emerald-500 text-white' }
      : { label: 'TẮT', color: 'bg-rose-500 text-white' };
  }, [status]);

  const handleModeChange = async (event) => {
    const nextMode = event.target.value;
    setMode(nextMode);
    await onSendCommand('set_pump_mode', { mode: nextMode });
  };

  const handleThresholdApply = async () => {
    await onSendCommand('set_humidity_threshold', { threshold: Number(threshold) });
  };

  const handleScheduleApply = async () => {
    await onSendCommand('set_schedule', {
      start_hour: Number(schedule.start_hour),
      start_min: Number(schedule.start_min),
      end_hour: Number(schedule.end_hour),
      end_min: Number(schedule.end_min),
      duration_sec: Number(schedule.duration_sec),
    });
  };

  return (
    <div className="grid gap-6 xl:grid-cols-2">
      <div className="rounded-3xl bg-white p-6 shadow-[0_20px_45px_rgba(15,23,42,0.18)]">
        <h2 className="text-xl font-semibold text-slate-900 mb-6">💧 Máy Bơm</h2>
        <div className="space-y-4">
          <div className="rounded-3xl bg-slate-50 p-5">
            <div className="text-sm text-slate-500">Trạng thái</div>
            <div className={`mt-4 inline-flex items-center gap-3 rounded-full px-4 py-2 ${pumpStatus.color}`}>
              <span className="h-3 w-3 rounded-full bg-white/80" />
              <span className="font-semibold">{pumpStatus.label}</span>
            </div>
          </div>
          <div className="grid gap-3 sm:grid-cols-2">
            <Button onClick={() => onSendCommand('set_pump_state', { state: 1 })} className="min-h-[3rem]">
              Bật ✓
            </Button>
            <Button variant="danger" onClick={() => onSendCommand('set_pump_state', { state: 0 })} className="min-h-[3rem]">
              Tắt ✗
            </Button>
          </div>
          <div className="rounded-3xl bg-slate-100 p-4 text-sm text-slate-600">
            Mode: <span className="font-semibold text-slate-900">{mode.toUpperCase()}</span>
          </div>
        </div>
      </div>

      <div className="rounded-3xl bg-white p-6 shadow-[0_20px_45px_rgba(15,23,42,0.18)]">
        <h2 className="text-xl font-semibold text-slate-900 mb-6">⚙️ Chế độ</h2>
        <div className="space-y-6">
          <div>
            <label className="mb-3 block text-sm font-medium text-slate-700">Chọn chế độ:</label>
            <select value={mode} onChange={handleModeChange} className="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-slate-900 outline-none transition focus:border-[#667eea]">
              {modeOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>

          {mode === 'auto' && (
            <div className="space-y-4 rounded-3xl bg-slate-50 p-5">
              <div className="text-sm font-medium text-slate-700">Ngưỡng độ ẩm (%)</div>
              <div className="flex flex-col gap-4 sm:flex-row sm:items-center">
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={threshold}
                  onChange={(e) => setThreshold(e.target.value)}
                  className="w-full cursor-pointer"
                />
                <input
                  type="number"
                  min="0"
                  max="100"
                  value={threshold}
                  onChange={(e) => setThreshold(e.target.value)}
                  className="w-24 rounded-2xl border border-slate-200 bg-white px-4 py-3 text-slate-900 outline-none"
                />
              </div>
              <Button onClick={handleThresholdApply}>Áp dụng</Button>
            </div>
          )}

          {mode === 'scheduled' && (
            <div className="space-y-4 rounded-3xl bg-slate-50 p-5">
              <div className="grid gap-4 sm:grid-cols-2">
                <div>
                  <label className="mb-2 block text-sm font-medium text-slate-700">Giờ bắt đầu</label>
                  <div className="grid gap-3 sm:grid-cols-2">
                    <input
                      type="number"
                      min="0"
                      max="23"
                      value={schedule.start_hour}
                      onChange={(e) => setSchedule((prev) => ({ ...prev, start_hour: e.target.value }))}
                      className="rounded-2xl border border-slate-200 bg-white px-4 py-3 text-slate-900 outline-none"
                    />
                    <input
                      type="number"
                      min="0"
                      max="59"
                      value={schedule.start_min}
                      onChange={(e) => setSchedule((prev) => ({ ...prev, start_min: e.target.value }))}
                      className="rounded-2xl border border-slate-200 bg-white px-4 py-3 text-slate-900 outline-none"
                    />
                  </div>
                </div>
                <div>
                  <label className="mb-2 block text-sm font-medium text-slate-700">Giờ kết thúc</label>
                  <div className="grid gap-3 sm:grid-cols-2">
                    <input
                      type="number"
                      min="0"
                      max="23"
                      value={schedule.end_hour}
                      onChange={(e) => setSchedule((prev) => ({ ...prev, end_hour: e.target.value }))}
                      className="rounded-2xl border border-slate-200 bg-white px-4 py-3 text-slate-900 outline-none"
                    />
                    <input
                      type="number"
                      min="0"
                      max="59"
                      value={schedule.end_min}
                      onChange={(e) => setSchedule((prev) => ({ ...prev, end_min: e.target.value }))}
                      className="rounded-2xl border border-slate-200 bg-white px-4 py-3 text-slate-900 outline-none"
                    />
                  </div>
                </div>
              </div>
              <div>
                <label className="mb-2 block text-sm font-medium text-slate-700">Thời gian chạy (giây)</label>
                <input
                  type="number"
                  min="1"
                  max="3600"
                  value={schedule.duration_sec}
                  onChange={(e) => setSchedule((prev) => ({ ...prev, duration_sec: e.target.value }))}
                  className="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-slate-900 outline-none"
                />
              </div>
              <Button onClick={handleScheduleApply}>Áp dụng Lịch</Button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
