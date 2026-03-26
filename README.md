# IoT Data Ingestion & Streaming Service

A FastAPI-based backend for user management, IoT data ingestion, historical/latest retrieval, and real-time updates over WebSockets. The solution uses MongoDB for persistence, Redis Pub/Sub for WebSocket fan-out, JWT authentication, and Docker for local setup.

## Tech Stack

- Python 3.10+ / FastAPI / async APIs
- MongoDB with PyMongo Async API
- Redis Pub/Sub for real-time broadcasting
- JWT authentication for REST and WebSockets
- Docker + Docker Compose for local environment setup

## Implemented Scope

### Authentication
- `POST /auth/signup` 
- `POST /auth/login`

### User Management
- `POST /users`
- `PUT /users/{user_id}`
- `GET /users/{user_id}`

### IoT Data
- `POST /iot/data`
- `GET /users/{user_id}/iot/latest`
- `GET /users/{user_id}/iot/history?limit=50`

### WebSockets
- `WS /ws/ingest?token=<JWT>`
- `WS /ws/subscribe?user_id=<USER_ID>&token=<JWT>`

## Quick Setup

### Option 1 — Docker Compose
```bash
cp .env.example .env
docker compose up -d --build
```
The application becomes available at `http://localhost:8000/docs`, with MongoDB on `localhost:27017` and Redis on `localhost:6379` in the local Docker setup. 

### Option 2 — Local Run
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
For non-Docker local execution, `.env` should point to local MongoDB and Redis instances if they are not running in containers. 

## Auth Flow

1. Sign up (optional) or log in to obtain a JWT access token.
2. Use the token for REST APIs as `Authorization: Bearer <JWT>`. 
3. Use the token for WebSockets via query params (`?token=<JWT>`) or handshake header if the client supports it. 
4. A bootstrap admin account is created from `.env`, so the default `admin/password` login works immediately in local setup. 

### Login Example
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "password"}'
```
Expected response:
```json
{
  "access_token": "<JWT>",
  "token_type": "bearer"
}
```
This matches the assignment’s JWT-based authentication requirement and the implemented project flow.

## REST API Examples

### Create User
```bash
curl -X POST http://localhost:8000/users \
  -H "Authorization: Bearer <JWT>" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "U1001", "name": "Test User", "status": "active"}'
```


### Ingest IoT Data
```bash
curl -X POST http://localhost:8000/iot/data \
  -H "Authorization: Bearer <JWT>" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "U1001", "metric_1": 34.5, "metric_2": 78, "metric_3": 1, "timestamp": 1710000100}'
```


### Fetch Latest Data
```bash
curl -H "Authorization: Bearer <JWT>" \
  http://localhost:8000/users/U1001/iot/latest
```


## WebSocket Examples

### Subscribe to a User Stream
```text
ws://localhost:8000/ws/subscribe?user_id=U1001&token=<JWT>
```
Whenever new data is ingested for `U1001`, the subscriber receives a `NEW_DATA` event.

### Ingest via WebSocket
```text
ws://localhost:8000/ws/ingest?token=<JWT>
```
Send payload:
```json
{
  "user_id": "U1001",
  "metric_1": 34.5,
  "metric_2": 78,
  "metric_3": 1,
  "timestamp": 1710000100
}
```
The ingest socket returns `INGESTED`, and matching subscribers receive `NEW_DATA` for the same `user_id`.

## Validation Rules

- `metric_1`: `0–100`
- `metric_2`: `0–200`
- `timestamp` must not be in the future
- target managed user must exist and be `active`

## Design Decisions

- **FastAPI + async architecture:** chosen to support both REST and WebSocket flows cleanly.
- **Separate auth accounts and managed IoT users:** keeps authentication concerns separate from business user entities. 
- **Redis Pub/Sub for fan-out:** enables WebSocket updates to scale beyond a single in-memory process.
- **Environment-driven configuration:** secrets and connection strings are stored in `.env`, not hardcoded. 
- **Strict response models:** internal DB-only fields like `_id` are not returned to clients. 
- **Timestamp uniqueness not enforced:** this is an intentional design choice because the assignment does not require `(user_id, timestamp)` uniqueness.

## Testing
```bash
pip install -r requirements-dev.txt
python -m pytest -q
```
