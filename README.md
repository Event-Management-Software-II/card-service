# card-service

Mastercard simulator service. It uses Flask for the HTTP API and Prisma as the ORM against its own PostgreSQL database.

## Setup

```bash
cp .env.example .env
pip install -r requirements.txt
prisma generate
prisma db push
python run.py
```

Main variables:

```env
DATABASE_URL="postgresql://mc_user:mc_password@localhost:5442/mastercard_db"
FLASK_DEBUG=false
```

## Endpoints

| Method | Route | Description |
| --- | --- | --- |
| GET | `/health` | Service health |
| POST | `/api/validate` | Validate `pan` and `cvv` for the orchestrator |
| POST | `/api/charge` | Process and store a card charge |
| POST | `/process-payment` | Direct payment processing endpoint |
| GET | `/transactions` | List stored transactions |
