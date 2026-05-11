# Frontend Yolobit Dashboard

This `frontend/` folder contains the React + Vite frontend for the Yolobit dashboard.
It is fully decoupled from the backend and communicates with the API through `/api/status`, `/api/history`, and `/api/command`.

## Features

- React 19 + Vite frontend scaffold
- Tailwind CSS for styling
- Recharts charts for 30-day history visualization
- `react-hot-toast` notifications for command feedback
- React Router tabs for realtime dashboard and history view
- Axios service layer for backend API requests
- Unit tests using Vitest and Testing Library

## Local setup

1. Install dependencies:
   ```bash
   cd frontend
   npm install
   ```

2. Start the dev server:
   ```bash
   npm run dev
   ```

3. Open the URL shown by Vite, typically `http://localhost:5173`.

## Backend integration

The frontend expects a running backend API that provides:

- `GET /api/status` — current device status
- `GET /api/history` — historical sensor data
- `POST /api/command` — pump control commands

By default the frontend connects to `http://localhost:5000`.
To override this, set `VITE_API_BASE` before starting Vite:

```bash
VITE_API_BASE=http://localhost:5000 npm run dev
```

## Scripts

- `npm run dev` — start Vite development server
- `npm run build` — build production assets
- `npm run preview` — preview production build
- `npm run lint` — run ESLint
- `npm run test` — run unit tests once
- `npm run test:watch` — run tests in watch mode

## Folder structure

- `src/main.jsx` — React entrypoint
- `src/App.jsx` — app routing and top-level state
- `src/services/api.js` — Axios API client and request helpers
- `src/hooks/` — reusable data hooks for status and history polling
- `src/features/` — page and widget components
- `src/components/ui/` — shared UI primitives
- `src/setupTests.js` — test environment setup

## Notes

- The frontend is intentionally separate from backend logic.
- Use environment variable `VITE_API_BASE` to point to a different backend host.
- The history page fetches `/api/history` and renders sensor trends for temperature, humidity, soil moisture, and light level.
