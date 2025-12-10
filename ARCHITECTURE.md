# SMS Remarketing Microservice - Architecture

## System Design

```
Client App
    ↓ (HTTP + API Key)
FastAPI Server
    ↓
PostgreSQL + Twilio API
    ↑
Background Worker (processes triggers)
```

Optional: Redis for async queue processing

## Core Components

### 1. FastAPI Server

Handles all HTTP requests. Authenticates via API keys, validates input, manages database transactions.

**Main files:**
- `src/sms_remarketing/main.py` - Entry point
- `src/sms_remarketing/api/` - Routes
- `src/sms_remarketing/middleware/auth.py` - Auth

### 2. Database (PostgreSQL)

**Tables:**
- `clients` - API keys, credits, account info
- `leads` - Contact info, custom fields (JSON)
- `templates` - Reusable SMS with `{{variables}}`
- `messages` - Send history, status, Twilio SID
- `triggers` - Automation rules (new_lead, lead_age, webhook)

All tables have foreign keys with cascading deletes. Indexed on `api_key`, `client_id`, `status`.

### 3. Twilio Integration

Sends SMS via Twilio API. On send:
1. Check credits
2. Create message record
3. Call Twilio
4. Save SID and status
5. Deduct credit

Errors logged to `message.error_message`. Credits deducted regardless of success (attempt counts).

### 4. Background Worker

Processes scheduled triggers. Runs as separate process with Python `schedule` library.

**Trigger types:**
- `new_lead` - Manual integration needed
- `lead_age` - Runs daily at 9 AM, checks leads created N days ago
- `webhook` - Via API endpoint (planned)

**Files:**
- `src/sms_remarketing/workers/worker.py`
- `src/sms_remarketing/workers/trigger_processor.py`

## Key Flows

### Manual SMS Send

```
1. POST /messages/send with API key
2. Validate key → load client
3. Check credits >= 1
4. Create message record (status: pending)
5. Deduct 1 credit
6. Send via Twilio
7. Update status (sent/failed) + save SID
8. Return response
```

### Automated Trigger (Lead Age)

```
1. Worker runs daily (9 AM)
2. Find active lead_age triggers
3. For each: query leads created N days ago
4. For each matching lead:
   - Render template
   - Check credits
   - Send SMS
   - Log message
```

## Authentication

API key in `X-API-Key` header. Format: `sk_<32-char-token>` generated with `secrets.token_urlsafe()`.

Flow:
1. Extract key from header
2. Query database
3. Verify client exists and is active
4. Attach to request
5. Proceed

Errors: 401 for missing/invalid, 403 for inactive.

## Credits

1 credit = 1 SMS. Deducted before sending.

Add credits via `POST /credits/add`. Should integrate with payment processor in production.

## Templates

Use `{{variable}}` syntax:
```
Hi {{first_name}}, welcome!
```

Variables from lead fields (first_name, last_name, etc.) or `custom_fields` JSON.

## Scaling

**API:** Stateless, run multiple instances behind load balancer

**Workers:** Run multiple with distributed locks (Redis) to prevent duplicates

**Database:** Add read replicas, connection pooling (pgbouncer), partition large tables

**Queue:** Use RQ with Redis for async processing

## Security (Production)

- Add admin auth to `/clients` endpoints
- Integrate `/credits/add` with payments
- Add rate limiting
- Force HTTPS
- Set `DEBUG=False`
- Configure specific CORS origins

## Monitoring

Add:
- Structured logging (JSON)
- Metrics (request rate, SMS success rate, credit usage)
- Error tracking (Sentry)
- `/health` endpoint checks

## Future Work

- Webhook triggers
- Bulk SMS endpoint
- Scheduled sends
- Analytics dashboard
- A/B testing
- Opt-out management
- MMS support
- Two-way SMS
- Multi-language templates

## Deployment

Set env vars, use managed PostgreSQL, configure CORS, set `DEBUG=False`.

Run API and worker as separate services (systemd, Docker, or platform like Railway/Render).

## Performance

- API latency: 100-300ms (includes Twilio call)
- With async queue: 10-50ms response
- Throughput: ~10-20 SMS/sec (Twilio limited), 100+ req/sec with queue
- Resources: ~50-100MB RAM per API worker, ~30-50MB for background worker
