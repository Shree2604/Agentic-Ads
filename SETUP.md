# AgenticAds Setup Guide

This guide covers the complete setup for both the **FastAPI + MongoDB** backend and the **React** frontend.

Refer to `SETUP.md` whenever you need the complete end-to-end environment instructions.

Quick start commands:

```bash
# Frontend
npm install
npm run dev

# Backend
cd backend
pip install -r requirements.txt
- Local instance: start `mongod`
- Atlas: ensure the cluster is reachable and the URI in `.env` is correct

### Start the API Server

```bash
python main.py
```

The API will be available at `http://localhost:8000`.

### Available Endpoints
- `GET /api/generation-history`
- `POST /api/generation-history`
- `GET /api/feedback`
- `POST /api/feedback`
- `GET /api/dashboard/stats`
- `GET /api/dashboard/charts`

Sample data is seeded automatically on first run if the collections are empty.

---

## Frontend (React + Vite)

### Prerequisites
- Node.js 16+
- npm or yarn

### Installation

```bash
npm install
```

### Start the Development Server

```bash
npm run dev
```

The app runs at `http://localhost:5173`.

### Production Build

```bash
npm run build
npm run preview
```

---

## Integration Notes

- The frontend expects the backend at `http://localhost:8000`
- CORS is already enabled for `localhost:5173`
- Ensure MongoDB is running before starting the API
- The React app uses the backend for generation history, feedback, and admin analytics data

---

## Troubleshooting

- **Backend fails to start**: verify Python version and that dependencies installed correctly
- **MongoDB connection error**: confirm the `MONGODB_URL` value and that MongoDB is running
- **Frontend cannot reach API**: ensure backend is running on port 8000 and CORS origins match the frontend URL

You're now ready to run AgenticAds locally with a fully integrated backend and frontend setup.
