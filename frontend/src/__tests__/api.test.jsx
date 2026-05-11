import { describe, expect, it, vi } from 'vitest';
import { client, sendCommand } from '../services/api';

describe('API service', () => {
  it('gọi đúng payload khi gửi lệnh set_pump_state', async () => {
    const postSpy = vi.spyOn(client, 'post').mockResolvedValue({ data: { status: 'queued' } });

    const payload = { state: 1 };
    await sendCommand('set_pump_state', payload);

    expect(postSpy).toHaveBeenCalledWith('/api/command', {
      command: 'set_pump_state',
      params: payload,
    });

    postSpy.mockRestore();
  });
});
