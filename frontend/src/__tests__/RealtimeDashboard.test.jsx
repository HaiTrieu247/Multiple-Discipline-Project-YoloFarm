import { render, screen } from '@testing-library/react';
import RealtimeDashboard from '../features/RealtimeDashboard';

test('hiển thị dữ liệu cảm biến đúng với mock data', () => {
  const mockStatus = {
    temperature: 24.7,
    humidity: 58.2,
    soil_moisture: 44,
    light_level: 1890,
    pump_state: 1,
    pump_mode: 'auto',
    humidity_threshold: 50,
    timestamp: 1710000000,
  };

  render(<RealtimeDashboard status={mockStatus} loading={false} error={null} />);

  expect(screen.getByText('24.7°C')).toBeInTheDocument();
  expect(screen.getByText('58.2%')).toBeInTheDocument();
  expect(screen.getByText('44%')).toBeInTheDocument();
  expect(screen.getByText('1890')).toBeInTheDocument();
});
