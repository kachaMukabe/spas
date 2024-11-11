from fastapi import APIRouter, Query, Response
from typing import Union
from config import Config
from models.whatsapp_models import WebhookMessage
from services import handle_messages

router = APIRouter()


@router.get("/webhook")
def verify_webhook(
    mode: Union[str, None] = Query(default=None, alias="hub.mode"),
    token: Union[str, None] = Query(default=None, alias="hub.verify_token"),
    challenge: Union[str, None] = Query(default=None, alias="hub.challenge"),
):
    if mode == "subscribe" and token == Config.VERIFY_TOKEN:
        return Response(challenge, status_code=200)
    return Response(status_code=403)


@router.post("/webhook")
async def handle_inbound_message(payload: WebhookMessage):
    print("Incoming: ", payload)
    changes = payload.entry[0].changes
    change_field = changes[0].field
    metadata = changes[0].value.metadata
    contacts = changes[0].value.contacts
    messages = changes[0].value.messages
    # statuses = changes[0].value.statuses if changes[0].value.statuses else None
    if messages:
        print("Handle message")
        await handle_messages(messages, metadata)
    return Response(status_code=200)
