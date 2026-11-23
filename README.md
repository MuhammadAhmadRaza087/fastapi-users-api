# Users API (FastAPI)

Simple FastAPI service with CRUD for dummy users and a health check.
Uses SQLite, so there is nothing else to install. 25 dummy users are added on first start.

## Endpoints

| Method | Path | What it does |
|---|---|---|
| GET | `/health` | App + database check. `200` when healthy, `503` when the DB fails |
| GET | `/health/live` | App is running (no DB check) |
| GET | `/users` | List users. Query: `skip`, `limit` (max 100), `q` (search name/email), `is_active` |
| GET | `/users/{id}` | One user |
| POST | `/users` | Create user |
| PUT | `/users/{id}` | Replace user (all fields) |
| PATCH | `/users/{id}` | Update some fields |
| DELETE | `/users/{id}` | Delete user |

Swagger UI: `/docs`

User body:

```json
{ "name": "Ali Khan", "email": "ali@example.com", "age": 25, "is_active": true }
```

`name` and `email` are required on POST and PUT. Emails are unique (duplicate gives `409`).

## Run locally

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate    Linux/macOS: source .venv/bin/activate
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
pytest
```

Open http://127.0.0.1:8000/docs

## Deploy on an Ubuntu server (e.g. Oracle Cloud)

```bash
sudo apt update && sudo apt install -y git python3-venv
cd ~ && git clone https://github.com/MuhammadAhmadRaza087/fastapi-users-api.git
cd fastapi-users-api
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

# run as a service (starts on boot, restarts on crash)
sudo cp deploy/users-api.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now users-api
curl localhost:8000/health
```

The service file assumes user `ubuntu` and the repo at `/home/ubuntu/fastapi-users-api`.
Change both in `deploy/users-api.service` if yours differ.

### Open port 8000 to the internet (optional)

1. OCI Console → your instance → Subnet → Security List → **Add Ingress Rule**:
   source `0.0.0.0/0`, TCP, destination port `8000`.
2. On the server (Oracle Ubuntu images block ports with iptables by default):

   ```bash
   sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 8000 -j ACCEPT
   sudo netfilter-persistent save
   ```

Then open `http://<server-ip>:8000/docs`.

There is no authentication: anyone who can reach the port can create and delete users.
Fine for dummy data; do not store anything real.

### Update after a new push

```bash
cd ~/fastapi-users-api && git pull
.venv/bin/pip install -r requirements.txt
sudo systemctl restart users-api
```

### Useful commands

```bash
systemctl status users-api
journalctl -u users-api -f
.venv/bin/python -m app.seed --reset   # wipe and re-add dummy users
```

## Settings (environment variables)

| Name | Default | |
|---|---|---|
| `DATABASE_URL` | `sqlite:///./data/app.db` | Any SQLAlchemy URL |
| `SEED_ON_STARTUP` | `true` | Add dummy users if the table is empty |
| `SEED_COUNT` | `25` | How many dummy users |
