# Airline Ticketing System

A Flask + MySQL web app for booking flights, managing airline flights, and leaving reviews. Customers can register, search flights, purchase tickets, cancel upcoming trips, review flights they've taken, and see their spending. Airline staff can create flights, change flight status, add airports and airplanes, and schedule maintenance.

Built with production practices: bcrypt-hashed passwords, CSRF protection, secure sessions, pooled SQLAlchemy connections, parameterized queries, containerized deployment via Docker, and a pytest suite gated by GitHub Actions CI.

## Table of contents

- [Quick start (Docker)](#quick-start-docker)
- [Local development](#local-development)
- [Configuration](#configuration)
- [Testing](#testing)
- [Project layout](#project-layout)
- [Security notes](#security-notes)
- [Production deployment](#production-deployment)

## Quick start (Docker)

**Use this if you just want to run the app** — to click around, demo it, or verify it works. Everything (Python, MySQL, gunicorn) runs inside containers, so there's no local Python or MySQL setup. Trade-off: changing Python code requires rebuilding the image (`docker compose up --build`), which is slow. If you're actively writing code, use [Local development](#local-development) instead.

Prereqs: Docker Desktop or Docker Engine + Compose plugin.

```bash
cp .env.example .env
# Edit .env: at minimum set SECRET_KEY (64+ random chars) and the MYSQL_* + DATABASE_URL passwords.
python -c "import secrets; print(secrets.token_urlsafe(64))"   # generate a SECRET_KEY

docker compose up --build -d
```

The app is now at http://localhost:8000. The MySQL container will initialize the schema from `db/schema.sql` on first boot.

### Stopping and managing the stack

```bash
docker compose down           # stop both containers (data persists in the volume)
docker compose down -v        # stop AND wipe the database (fresh start next time)
docker compose logs -f web    # tail the app logs
docker compose logs -f mysql  # tail the MySQL logs
docker compose ps             # see what's running
docker compose up -d          # start again (no rebuild — uses existing image)
docker compose up --build -d  # rebuild the image, e.g. after changing Python code
```

`docker compose down` stops the containers but Docker Desktop itself keeps running in the background (using some RAM). To fully quit it, click the whale icon in the macOS menu bar &rarr; **Quit Docker Desktop**.

## Local development

**Use this if you're editing the code.** The Flask app runs directly on your machine via `flask --debug`, so saving a `.py` file hot-reloads the server and you can set breakpoints in your editor. MySQL still runs in a container (easier than installing MySQL locally). Fast feedback loop; requires a Python venv and `pip install`.

Prereqs: Python 3.11, a local or Docker MySQL 8.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt

# Bring up MySQL (either your own instance or via docker compose up mysql -d)
# Load the schema:
mysql -uroot -p air_ticket_system < db/schema.sql

cp .env.example .env
# Set FLASK_ENV=development and edit DATABASE_URL (or DB_* vars) to point at your MySQL.

flask --app wsgi run --debug --port 5000
```

The app is at http://localhost:5000.

### Stopping local dev

```bash
# In the terminal running flask:
Ctrl-C                        # stops the Flask dev server

# If you started MySQL via docker compose:
docker compose stop mysql     # stop MySQL (keeps the volume)
docker compose down -v        # stop AND wipe MySQL data

deactivate                    # leave the Python venv when you're done
```

## Configuration

All configuration is via environment variables. `.env` is loaded automatically
by `wsgi.py` (via `python-dotenv`).

| Variable          | Required in     | Purpose                                  |
| ----------------- | --------------- | ---------------------------------------- |
| `FLASK_ENV`       | always          | `production`, `development`, `testing`   |
| `SECRET_KEY`      | production      | Signs the session cookie                 |
| `DATABASE_URL`    | production      | SQLAlchemy URL for the app DB            |
| `DB_HOST/PORT/USER/PASSWORD/NAME` | development (fallback) | Assembled into a URL if `DATABASE_URL` isn't set |
| `TEST_DATABASE_URL` | testing       | Separate DB used by pytest               |
| `LOG_LEVEL`       | optional        | `DEBUG`, `INFO` (default), `WARNING`, ...|

`ProductionConfig` refuses to start if `SECRET_KEY` or `DATABASE_URL` is unset.

## Testing

Tests run against a real MySQL. Point `TEST_DATABASE_URL` at a database you WANT to WIPE.

```bash
export TEST_DATABASE_URL="mysql+pymysql://user:pw@127.0.0.1:3306/air_ticket_system_test?charset=utf8mb4"
pytest
```

CI (`.github/workflows/ci.yml`) runs `ruff check`, `ruff format --check`, `mypy`, and `pytest --cov` against a MySQL 8 service container on every push and PR.

## Project layout

```
.
├── app/
│   ├── __init__.py            # app factory + logging + error handlers
│   ├── config.py              # Production/Development/Testing configs
│   ├── extensions.py          # SQLAlchemy, Bcrypt, CSRFProtect singletons
│   ├── security.py            # password hashing, decorators, PAN masking
│   ├── blueprints/
│   │   ├── main.py            # /
│   │   ├── auth.py            # customer + staff login/register/logout
│   │   ├── customer.py        # dashboard, search, purchase, cancel, review
│   │   └── staff.py           # dashboard, flight/airplane/airport/maintenance
│   ├── templates/             # Jinja2 templates (with CSRF tokens)
│   └── static/                # CSS
├── db/schema.sql              # DDL loaded at container init / manual setup
├── tests/                     # pytest suite (real MySQL fixtures)
├── .github/workflows/ci.yml   # ruff + mypy + pytest
├── Dockerfile                 # non-root user, gunicorn, healthcheck
├── docker-compose.yml         # mysql + web
├── wsgi.py                    # gunicorn entrypoint
├── requirements.txt           # runtime deps
├── requirements-dev.txt       # + test/lint/type deps
├── pyproject.toml             # ruff / mypy / pytest config
├── .env.example               # copy → .env
└── README.md
```

## Security notes

- **Passwords**: bcrypt (Flask-Bcrypt) with per-hash salt.
- **Session cookies**: `HttpOnly`, `SameSite=Lax`, `Secure` in production; the Flask secret key is required from `SECRET_KEY` env.
- **CSRF**: `Flask-WTF` `CSRFProtect` enabled globally; every POST form includes `{{ csrf_token() }}`.
- **SQL**: All queries use bound parameters via `SQLAlchemy text()`. No string concatenation.
- **User enumeration**: Login errors are a single "invalid email or password" message and constant-time password verification (even on unknown users).
- **Auth guards**: `customer_required` / `staff_required` decorators on every authenticated route; ticket cancellation now requires ownership.
- **Ticket ID generation**: `secrets.token_hex(8)` instead of `COUNT(*) + 100` (which had a race and reused IDs after deletes).
- **Payment data**: Only the last 4 digits of the card are stored in `Purchase.card_last4`. For a real deployment, remove that column entirely and integrate a payment processor (Stripe, Braintree). The current app is **not** PCI-compliant — do not use it to accept real cards.
- **Reviews**: Only allowed on flights the reviewer actually purchased and that have already departed. Duplicate reviews upsert instead of failing.
- **Headers**: `X-Content-Type-Options`, `X-Frame-Options`, a strict CSP, and `Referrer-Policy` are set on every response.
- **Reverse proxy**: `ProxyFix` trusts one hop so `X-Forwarded-*` headers from an ingress work correctly.
- **Secrets**: Nothing sensitive is committed. `.env` is git-ignored and only `.env.example` (with placeholders) is checked in.

## Production deployment

The included `docker-compose.yml` is suitable for a single-host deployment.
For anything larger:

1. Terminate TLS at a reverse proxy (nginx / Caddy / cloud LB) in front of `web:8000` — the app expects HTTPS and sets `SESSION_COOKIE_SECURE=True`.
2. Run MySQL as a managed service (RDS, Cloud SQL, PlanetScale) rather than the container. Point `DATABASE_URL` at it.
3. Set a real `SECRET_KEY` in the platform's secret store (never commit the value or bake it into an image).
4. Scale horizontally by running more `web` containers behind the LB — the app is stateless apart from the DB.
5. Ship logs to a central aggregator; gunicorn writes access + error logs to stdout.
6. Do **not** enable the sample card storage in a real deployment; wire in a payment processor and drop `Purchase.card_last4`.

Health check endpoint: `GET /healthz` — returns `200 {"status": "ok"}` when the DB is reachable, `503` otherwise. The Docker healthcheck already uses it.

## License

MIT &mdash; see [LICENSE](LICENSE). Not intended to handle real payment data or PII in production; wire in a payment processor first.