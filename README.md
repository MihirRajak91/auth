# Simple MongoDB Auth API

This project exposes a lightweight Flask REST API that lets a frontend register and log in users using an email, password, and role. The code is organised inside an `auth` package so it can be dropped into other projects with minimal wiring. User documents are stored in MongoDB with unique `user_id` values and hashed passwords, and JWTs are issued to authenticate calls across services.

## Requirements

- Python 3.10+
- Running MongoDB server (defaults to `mongodb://localhost:27017/`)

## Setup

1. Optional: point the API at a different database by setting the `MONGODB_URI` environment variable, e.g.
   ```bash
   export MONGODB_URI="mongodb://user:pass@localhost:27017/?authSource=admin"
   ```
2. Set a strong signing secret for JWTs in production:
   ```bash
   export JWT_SECRET="a-very-long-random-string"
   # Optional overrides:
   export JWT_ALGORITHM="HS256"
   export JWT_EXP_SECONDS="3600"
   ```
3. Install dependencies with Poetry:
   ```bash
   poetry install
   ```

## Running the API

Start the development server:

```bash
poetry run auth-server
# or
poetry run python server.py
```

The server listens on `http://127.0.0.1:5000` by default.

## Endpoints

- `GET /healthz` — simple health check.
- `POST /register`
  - Request JSON: `{"email": "...", "password": "...", "role": "...", "organization_id": "..."}`
  - Response `201`: registration success with `user_id`, `email`, `role`, and a `token`.
  - Response `409`: email already registered.
- `POST /login`
  - Request JSON: `{"email": "...", "password": "..."}`.
  - Response `200`: login success with `user_id`, `email`, `role`, and a `token`.
  - Response `401`: incorrect password.
  - Response `404`: account not found.
- `GET /me`
  - Requires `Authorization: Bearer <token>` header.
  - Response `200`: the JWT claims (`user_id`, `email`, `role`) and expiry.
  - Response `401`: missing, invalid, or expired token.

Passwords are hashed with bcrypt before being stored. Error responses include a short description and (when applicable) field validation details so the frontend can provide friendly messaging.

The `token` returned from `/login` or `/register` is a signed JWT that other services can verify with the shared `JWT_SECRET` to authenticate the caller. Include it in the `Authorization` header for subsequent requests: `Authorization: Bearer <token>`. Tokens include the caller's `organization_id` so downstream services can enforce tenant-level access control.

## Reusing the Auth package

To integrate with another Flask project:

1. Copy the `auth` folder into your project.
2. Import and register the blueprint:
   ```python
   from auth import create_app

   app = create_app()
   # or if you already have a Flask app instance:
   from auth.config import load_settings
   from auth.routes import bp as auth_bp

   app.config["AUTH_SETTINGS"] = load_settings()
   app.register_blueprint(auth_bp)
   ```
3. Ensure the required environment variables (`MONGODB_URI`, `JWT_SECRET`, etc.) are set.
