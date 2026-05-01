# LogMile

LogMile is a full-stack Django + React MVP for planning long-haul truck trips under FMCSA Hours of Service constraints.

It accepts:
- Current location
- Pickup location
- Dropoff location
- Trip start time
- Current cycle used
- Optional cycle rule (`70_8` or `60_7`)

It returns:
- A routed map using OpenRouteService and OpenStreetMap
- Operational stops such as pickup, fuel, breaks, rests, and dropoff
- Day-by-day ELD log sheets rendered visually as SVG

## Stack

- Backend: Django + Django REST Framework
- API docs: drf-spectacular
- Frontend: React + Vite + TypeScript + Tailwind CSS
- Map: Leaflet + OpenStreetMap
- Routing/geocoding: OpenRouteService
- Containers: Docker + docker-compose

## Project Structure

```text
backend/
  config/
  trips/
frontend/
  src/
docker-compose.yml
```

## Environment

Copy `.env.example` to `.env` and provide a valid OpenRouteService API key.

Required variables:

```env
DJANGO_SECRET_KEY=replace_me
DJANGO_DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
CSRF_TRUSTED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
OPENROUTESERVICE_API_KEY=replace_me
SQLITE_PATH=db.sqlite3
REDIS_URL=redis://redis:6379/1
VITE_DEV_API_PROXY_TARGET=http://localhost:8000
```

## Local Development

### Backend

```bash
cd backend
poetry install
poetry run python manage.py migrate
poetry run python manage.py runserver
```

### Frontend

```bash
cd frontend
npm install
npm run typecheck
npm run dev
```

The Vite dev server proxies `/api` to the backend target defined by `VITE_DEV_API_PROXY_TARGET`, so frontend code can use same-origin API paths in both development and production.

### Docker

```bash
docker compose up --build
```

Docker Compose now runs a lean MVP stack:
- `redis` for shared caching and throttle storage
- `backend` with a local SQLite database file for Django migrations and built-in tables
- `backend` under Gunicorn
- `frontend` as built static assets served by Nginx on `http://localhost:5173`
- backend is still reachable directly on `http://localhost:8000`

## API Endpoints

- `GET /api/health/`
- `POST /api/trip/plan/`
- `GET /api/schema/`
- `GET /api/docs/`
- `GET /api/redoc/`

Example request:

```json
{
  "current_location": "Chicago, IL",
  "pickup_location": "St. Louis, MO",
  "dropoff_location": "Dallas, TX",
  "trip_start_at": "2026-05-01T11:45:00-05:00",
  "current_cycle_used": 20,
  "cycle_rule": "70_8"
}
```

## Backend Notes

- `trips/views.py` is intentionally thin. It validates request data and delegates orchestration to `trips/services/trip_planner.py`.
- `trips/maps/` contains the OpenRouteService integration, geometry helpers, and stop-coordinate hydration logic.
- `trips/hos/` contains the pure Python HOS scheduler split into constants, typed internal models, reusable helpers, and the planner loop.
- `trips/types.py` and `trips/utils.py` hold shared response shapes, request dataclasses, and numeric helpers used across the backend.
- Route geocoding and directions are cached through Django’s cache layer. With `REDIS_URL` set, those cache entries are shared across instances.
- The trip planning endpoint is rate limited with burst and sustained throttles to protect the ORS dependency.
- Postgres was removed from the default setup because the MVP does not persist domain data. Django uses SQLite locally for its built-in tables.

## Frontend Notes

- `TripForm.tsx` collects planner inputs.
- `RouteMap.tsx` renders the route polyline and operational markers.
- `EldLogSheet.tsx` draws each daily log with SVG so duty-status lines land precisely on the grid.
- Tailwind theme tokens live in `frontend/tailwind.config.ts`, while shared utility bundles live in `frontend/src/constants/ui.ts`.

## Current MVP Limits

- No authentication
- No persisted trip history
- No PDF export yet
- No fuel-station search; fuel stops are placed logically by distance
- No advanced FMCSA exceptions or sleeper berth split rules
- Trip planning is still synchronous inside the request path; for very high traffic or long-running route providers, background jobs would be the next step
