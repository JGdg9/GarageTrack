# GarageTrack

GarageTrack helps you keep vehicle details, maintenance history, and costs in one place.

## Demo

- [https://garagetrack-demo.onrender.com/](https://garagetrack-demo.onrender.com/)
- [Open the API documentation](https://garagetrack-demo.onrender.com/docs)

The public demo uses sample data and is read-only.

## Features

- Add, edit, view, and remove vehicles.
- Record and manage vehicle maintenance.
- Review maintenance history and expenses.
- Use the API through the browser or `/docs`.

## Technologies

Python, FastAPI, Pydantic, SQLAlchemy, MySQL, HTML, CSS, JavaScript, and Pytest.

## Run locally on Windows

You need Python 3.12 or newer and MySQL 8 or newer.

Create the databases and local users in MySQL. Replace the example passwords with your own:

```sql
CREATE DATABASE garagetrack CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
CREATE DATABASE garagetrack_test CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;

CREATE USER 'garagetrack_app'@'127.0.0.1' IDENTIFIED BY 'change-this-password';
GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, INDEX, REFERENCES ON garagetrack.* TO 'garagetrack_app'@'127.0.0.1';

CREATE USER 'garagetrack_test'@'127.0.0.1' IDENTIFIED BY 'change-this-test-password';
GRANT ALL PRIVILEGES ON garagetrack_test.* TO 'garagetrack_test'@'127.0.0.1';
```

From the project folder, install the Python dependencies and create your local settings file:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --requirement .\backend\requirements.txt
Copy-Item .env.example .env
```

Edit `.env` with the passwords you used above. The example uses MySQL on port `3307`; change it if your server uses another port.

Initialize the database and start the app:

```powershell
Set-Location .\backend
..\.venv\Scripts\python.exe -m app.init_db
..\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Open [the app](http://127.0.0.1:8000) or [the API docs](http://127.0.0.1:8000/docs).

## Tests

From the project folder, run the backend tests:

```powershell
.\.venv\Scripts\python.exe -m pytest .\backend\tests\unit
.\.venv\Scripts\python.exe -m pytest .\backend\tests\integration
```

The integration tests use the separate MySQL database `garagetrack_test`.

Frontend checks require Node.js 24 or newer. Run them from `frontend`:

```powershell
npm ci
npm test
npm run lint
npm run format:check
```

## Project structure

- `backend/app/routers/` contains the API endpoints.
- `backend/app/services/` contains the vehicle and maintenance operations.
- `backend/app/models.py` defines the database tables.
- `backend/tests/` contains unit and MySQL integration tests.
- `frontend/` contains the HTML, CSS, and JavaScript.

![GarageTrack dashboard](frontend/assets/dashboard.png)
