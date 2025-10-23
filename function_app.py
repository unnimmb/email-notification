import json
import logging
from typing import Any, Dict

from azure.functions import FunctionApp, HttpRequest, HttpResponse, AuthLevel

from email_util.client import EmailClient
from email_util.models import EmailRequest
from email_util.config import get_settings

app = FunctionApp(http_auth_level=AuthLevel.FUNCTION)
settings = get_settings()

logging.basicConfig(level=getattr(logging, settings.log_level, logging.INFO))
logger = logging.getLogger("email_function")
_email_client: EmailClient | None = None

def get_client() -> EmailClient:
    global _email_client
    if _email_client is None:
        _email_client = EmailClient()
    return _email_client

@app.route(route="send-email", methods=["POST"], auth_level=AuthLevel.FUNCTION)
def send_email(req: HttpRequest) -> HttpResponse:
    try:
        body_bytes = req.get_body() or b"{}"
        payload: Dict[str, Any] = json.loads(body_bytes.decode("utf-8"))
    except Exception as e:
        return _json_response({"error": f"Invalid JSON: {str(e)}"}, 400)

    try:
        email_req = EmailRequest(
            to=payload.get("to", []),
            subject=payload.get("subject", "(no subject)"),
            body_text=payload.get("body_text"),
            body_html=payload.get("body_html"),
            cc=payload.get("cc", []),
            bcc=payload.get("bcc", []),
            reply_to=payload.get("reply_to"),
        )
        email_req.validate()
    except Exception as e:
        return _json_response({"error": str(e)}, 400)

    client = get_client()
    try:
        result = client.send(email_req)
        logger.info("Email sent via provider '%s' result=%s", settings.mail_provider, result)
    except Exception as e:
        logger.exception("Failed to send email")
        return _json_response({"error": str(e)}, 500)

    return _json_response({"status": "sent", "provider": settings.mail_provider, "result": result}, 200)

def _json_response(data: Dict[str, Any], status: int) -> HttpResponse:
    return HttpResponse(
        body=json.dumps(data),
        status_code=status,
        mimetype="application/json",
        headers={"Content-Type": "application/json"}
    )
