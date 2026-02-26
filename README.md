# Directory REST API

REST API for a directory of **Organizations**, **Buildings**, and **Activities**.  
Stack: **FastAPI** + **Pydantic** + **SQLAlchemy** + **Alembic**.

- All endpoints require the **X-API-Key** header.
- Responses are **JSON**.
- Activity tree is limited to **3 levels**.
- **Swagger UI**: `/docs` · **ReDoc**: `/redoc`.

---

## Quick start (local)

1. **Create virtualenv and install dependencies**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate   # Windows
   pip install -r requirements.txt
   ```

2. **Configure (optional)**
   - Copy `.env.example` to `.env` and set `API_KEY` and `DATABASE_URL` if needed.
   - Default: SQLite `./test.db`, API key `dev-api-key-change-in-production`.

3. **Run migrations and seed**
   ```bash
   alembic upgrade head
   python seed_data.py
   ```

4. **Start the API**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

5. **Open docs**
   - Swagger: http://localhost:8000/docs  
   - ReDoc: http://localhost:8000/redoc  

Use header: **X-API-Key**: `dev-api-key-change-in-production` (or your `API_KEY`).

---

## Deployment with Docker

### Using Docker Compose (recommended)

Runs the API and PostgreSQL in one command:

```bash
# Optional: set API key
set API_KEY=your-secret-api-key

docker-compose up --build
```

- API: http://localhost:8000  
- Migrations and seed run on startup.
- Database data is stored in a Docker volume.

### Using Docker only (external DB)

1. **Build image**
   ```bash
   docker build -t directory-api .
   ```

2. **Run with env**
   ```bash
   docker run -p 8000:8000 ^
     -e DATABASE_URL=postgresql://user:pass@host:5432/dbname ^
     -e API_KEY=your-api-key ^
     directory-api
   ```

To run migrations and seed before the app, use a custom command:

```bash
docker run -p 8000:8000 ^
  -e DATABASE_URL=postgresql://user:pass@host:5432/dbname ^
  -e API_KEY=your-api-key ^
  directory-api ^
  sh -c "alembic upgrade head && python seed_data.py && uvicorn app.main:app --host 0.0.0.0 --port 8000"
```

---

## API endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/organizations` | List organizations (optional: `building_id`, `activity_id`, `name`) |
| GET | `/api/organizations/by-building/{building_id}` | Organizations in a building |
| GET | `/api/organizations/by-activity/{activity_id}` | Organizations by exact activity |
| GET | `/api/organizations/by-activity-tree/{activity_id}` | Organizations by activity + descendants (e.g. "Food" → Food, Meat, Dairy) |
| GET | `/api/organizations/search-by-name?q=...` | Search by name (substring) |
| GET | `/api/organizations/in-area` | Organizations in radius or rectangle (`lat`, `lon`, `radius_km` or `min_lat`, `max_lat`, `min_lon`, `max_lon`) |
| GET | `/api/organizations/{id}` | Organization by ID |
| GET | `/api/buildings` | List buildings (optional bbox: `min_lat`, `max_lat`, `min_lon`, `max_lon`) |
| GET | `/api/buildings/in-area` | Buildings in radius or rectangle |
| GET | `/api/buildings/{id}` | Building by ID |
| GET | `/api/buildings/{id}/organizations` | Organizations in building |
| GET | `/api/activities` | List activities (flat) |
| GET | `/api/activities/tree` | Activities as tree (max 3 levels) |
| GET | `/api/activities/{id}` | Activity by ID |

All require header: **X-API-Key**: `<your API_KEY>`.

---

## Data model

- **Organization**: name, multiple phone numbers, one building, many activities.
- **Building**: address, latitude, longitude.
- **Activity**: name, tree (parent_id, level 1–3).

Test data includes buildings (e.g. Moscow, Blukhera, Saint Petersburg), an activity tree (Food → Meat/Dairy, Cars → Trucks/Passenger/Spare parts/Accessories), and organizations with phones and activity links.
