# Email Notification Azure Function (Python)

A minimal Azure Function (Python v2 programming model) providing an HTTP endpoint to send email notifications via SMTP or SendGrid.

## Folder Structure
```
EmailNotificationAzureFunction/
  host.json
  local.settings.json          # Local dev settings (do NOT deploy with secrets)
  requirements.txt             # Python dependencies
  function_app.py              # FunctionApp with HTTP route
  email_util/                  # Email abstraction
    __init__.py
    config.py
    models.py
    providers.py
    client.py
  tests/                       # (optional) unit tests
```

## Prerequisites
- Python 3.11 (recommended)
- Azure Functions Core Tools v4
- An SMTP server OR a SendGrid API key.

Install Core Tools (if needed):
```powershell
npm i -g azure-functions-core-tools@4 --unsafe-perm true
```

## Setup (Local)
```powershell
cd EmailNotificationAzureFunction
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
func start
```

## Environment Variables
Set in `local.settings.json` (Values section) for local; in Azure Function App Configuration for production:
| Variable | Description |
|----------|-------------|
| MAIL_PROVIDER | smtp (default) or sendgrid |
| DEFAULT_FROM_EMAIL | From address |
| SMTP_HOST | SMTP host (smtp provider) |
| SMTP_PORT | SMTP port (default 25) |
| SMTP_USERNAME | SMTP user (optional) |
| SMTP_PASSWORD | SMTP password (optional) |
| SMTP_STARTTLS | 1/0 enable STARTTLS (default 1) |
| SENDGRID_API_KEY | API key (SendGrid provider) |
| LOG_LEVEL | Logging level (INFO/DEBUG/WARN/ERROR) |

## HTTP Endpoint
Route: `POST /api/send-email`
Auth: Function key (append `?code=<FUNCTION_KEY>` when deployed). Local dev with `func start` may allow direct access.

### Sample Request
```json
{
  "to": ["recipient@example.com"],
  "subject": "Test Notification",
  "body_text": "Plain text body",
  "body_html": "<p>HTML body</p>",
  "cc": [],
  "bcc": [],
  "reply_to": "reply@example.com"
}
```
At least one of `body_text` or `body_html` is required.

### Curl Example (Local)
```powershell
curl -X POST http://localhost:7071/api/send-email ^
  -H "Content-Type: application/json" ^
  -d '{"to":["recipient@example.com"],"subject":"Hello","body_text":"Hi"}'
```

## Switching Provider
- SMTP: ensure `MAIL_PROVIDER=smtp` plus SMTP_* variables.
- SendGrid: set `MAIL_PROVIDER=sendgrid` and `SENDGRID_API_KEY`.

## Deployment Steps
1. Create Function App (Python runtime) in Azure.
2. Set Application Settings (env vars) under Configuration.
3. Deploy:
   ```powershell
   func azure functionapp publish <YourFunctionAppName>
   ```
4. Test:
   ```powershell
   curl -X POST "https://<YourFunctionAppName>.azurewebsites.net/api/send-email?code=<FUNCTION_KEY>" ^
     -H "Content-Type: application/json" ^
     -d '{"to":["recipient@example.com"],"subject":"Prod","body_text":"Hi from Azure"}'
   ```

## Responses
- 200: `{ "status": "sent", "provider": "smtp", "result": ... }`
- 400: `{ "error": "validation or JSON error" }`
- 500: `{ "error": "provider failure details" }`

## Logging
Adjust `LOG_LEVEL`. Logs visible locally in console; in Azure via App Insights (if configured) / Live Metrics.

## Extensibility
Add new provider in `providers.py` implementing `.send(EmailRequest)` and update `get_provider()` logic.

## Tests (Optional)
Create tests in `tests/` mocking `SMTPProvider` or `SendGridProvider` to assert JSON output.

## Security Notes
- Do not commit real API keys or passwords.
- Use Azure Key Vault references for secrets in production if possible.
- Keep auth level as `FUNCTION` unless you front the endpoint with APIM / AAD.

## Troubleshooting
| Symptom | Cause | Fix |
|---------|-------|-----|
| 500 provider failure | Bad SMTP creds, network issue | Check env vars, firewall, enable STARTTLS |
| 400 invalid email | Bad address format | Correct address; ensure domain valid |
| sendgrid package not installed | Missing dependency | `pip install sendgrid` (already in requirements) |
| Timeout connecting SMTP | Wrong host/port | Verify connectivity, open port |

## Next Enhancements
- Attachments support
- Retry logic / exponential backoff
- Structured logging to JSON
- Observability (App Insights custom traces)

---
Ready to send emails!
