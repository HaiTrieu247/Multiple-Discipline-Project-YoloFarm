# Frontend Yolobit Dashboard

This folder contains a separate frontend scaffold for the Yolobit dashboard.

## How to use

1. Run the backend API service first:
   ```bash
   uvicorn backend.app:app --reload
   ```
2. Open `frontend/index.html` in your browser.
3. The page will connect to `http://localhost:5000/api/status` and display device values.

## Notes

- The frontend is intentionally separated from backend logic.
- If you want, you can serve it with any static server such as `python -m http.server 8000`.
