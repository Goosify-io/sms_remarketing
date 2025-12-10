# SMS Remarketing Microservice

Send automated SMS messages to leads using Twilio. Built with FastAPI, PostgreSQL, and Redis.

## What it does

- Send SMS via API with templates
- Auto-send based on triggers (new leads, time-based, webhooks)
- Track credits (1 SMS = 1 credit)
- Async queue processing with Redis (optional)

## Stack

- Python 3.12+
- FastAPI
- PostgreSQL
- Redis (optional, for async)
- Twilio

## Setup

**1. Install dependencies**

```bash
uv sync
```

**2. Start services**

```bash
docker-compose up -d
```

**3. Configure**

Copy `.env.example` to `.env` and add your Twilio credentials:

```
TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_token
TWILIO_PHONE_NUMBER=+1234567890
```

**4. Run migrations**

```bash
uv run alembic upgrade head
```

**5. Start the server**

```bash
uv run python -m sms_remarketing.main
```

API runs at `http://localhost:8000`

**6. Start workers (optional)**

For background trigger processing:
```bash
uv run python -m sms_remarketing.workers.worker
```

For async SMS queue (requires Redis):
```bash
uv run python -m sms_remarketing.workers.rq_worker
```

## Usage

**Create a client**

```bash
curl -X POST http://localhost:8000/api/v1/clients/ \
  -H "Content-Type: application/json" \
  -d '{"name": "My Company", "email": "me@example.com", "initial_credits": 100}'
```

Save the `api_key` from the response.

**Add a lead**

```bash
curl -X POST http://localhost:8000/api/v1/leads/ \
  -H "X-API-Key: your_api_key" \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "+1234567890", "first_name": "John"}'
```

**Create a template**

```bash
curl -X POST http://localhost:8000/api/v1/templates/ \
  -H "X-API-Key: your_api_key" \
  -H "Content-Type: application/json" \
  -d '{"name": "Welcome", "content": "Hi {{first_name}}!"}'
```

**Send SMS**

```bash
curl -X POST http://localhost:8000/api/v1/messages/send \
  -H "X-API-Key: your_api_key" \
  -H "Content-Type: application/json" \
  -d '{"lead_id": 1, "template_id": 1, "variables": {"first_name": "John"}}'
```

**Setup automation**

New lead trigger:
```bash
curl -X POST http://localhost:8000/api/v1/triggers/ \
  -H "X-API-Key: your_api_key" \
  -H "Content-Type: application/json" \
  -d '{"name": "Welcome", "template_id": 1, "trigger_type": "new_lead"}'
```

7-day follow-up:
```bash
curl -X POST http://localhost:8000/api/v1/triggers/ \
  -H "X-API-Key: your_api_key" \
  -H "Content-Type: application/json" \
  -d '{"name": "Follow-up", "template_id": 2, "trigger_type": "lead_age", "config": {"days": 7}}'
```

## Docs

API docs at `http://localhost:8000/docs`

See `ARCHITECTURE.md` for system design details.

## Testing

```bash
uv run pytest
```

## Production notes

- Add admin auth to `/clients` endpoints
- Integrate payment system with `/credits/add`
- Use HTTPS
- Set `DEBUG=False`
- Add rate limiting
- Run multiple workers for scale
