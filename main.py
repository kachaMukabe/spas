import os
import httpx
from fastapi import FastAPI, Query, Response
from dotenv import load_dotenv
from typing import List, Union

from starlette.types import Message
from models import whatsapp_models as wm


load_dotenv()

app = FastAPI()

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
GRAPH_API_TOKEN = os.getenv("GRAPH_API_TOKEN")
RAPID_PRO_URL = os.getenv("RAPID_PRO_URL")


@app.get("/webhook")
def verify_webhook(
    mode: Union[str, None] = Query(default=None, alias="hub.mode"),
    token: Union[str, None] = Query(default=None, alias="hub.verify_token"),
    challenge: Union[str, None] = Query(default=None, alias="hub.challenge"),
):
    if mode == "subscribe" and token == VERIFY_TOKEN:
        return Response(challenge, status_code=200)
    return Response(status_code=403)


@app.post("/webhook")
async def handle_inbound_message(payload: wm.WebhookMessage):
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

async def handle_messages(messages: List[wm.Message], metadata: wm.MetaData):
    message = messages[0]
    match message.type:
        case "text":
            await send_to_rapid_pro(message.text.body, message.from_user)
        case "reaction":
            pass
        case "image":
            pass 
        case "interactive":
            await send_to_rapid_pro(message.interactive.list_reply.id, message.from_user)
        case "location":
            await send_to_rapid_pro(message.location.latitude+" "+message.location.longitude, message.from_user)
        case "order":
            await send_message(
                metadata.phone_number_id,
                message,
                "Your order has been placed. You will recieve a payment link shortly",
            )
        case _:
            pass

async def send_to_rapid_pro(text, sender):
    url = f"{RAPID_PRO_URL}/receive?text={text}&sender={sender}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        print(response)


async def send_message(business_number, message: wm.Message, response_txt: str):
    message_data = {
        "messaging_product": "whatsapp",
        "to": message.from_user,
        "text": {"body": response_txt},
        "context": {"message_id": message.id},
    }
    url = f"https://graph.facebook.com/v18.0/{business_number}/messages"
    headers = {"Authorization": f"Bearer {GRAPH_API_TOKEN}"}
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=message_data)
        response.raise_for_status()
