import httpx
import logging
from typing import List
from config import Config
from models.whatsapp_models import Message, MetaData, Section

logger = logging.getLogger(__name__)


async def send_to_rapidpro(phone_number: str, message: str):
    url = f"{Config.RAPID_PRO_URL}/receive?text={message}&sender={phone_number}"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url)
            response.raise_for_status()
            logger.info(f"Response: {response.json()}")
        except httpx.HTTPStatusError as e:
            logger.error(f"Error: {e}")
        except Exception as e:
            logger.error(f"Error: {e}")


async def send_rapid_message(to_user, response_text):
    message_data = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to_user,
        "type": "text",
        "text": {"body": response_text},
    }
    logger.info(message_data)
    url = f"https://graph.facebook.com/v20.0/{Config.BUSINESS_PHONE_ID}/messages"
    headers = {"Authorization": f"Bearer {Config.GRAPH_API_TOKEN}"}
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=message_data)
        response.raise_for_status()


async def send_interactive_list(
    to_user, header_text, text, footer_text, button_text, sections: List[Section]
):

    message_data = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to_user,
        "type": "interactive",
        "interactive": {
            "type": "list",
            "header": {"type": "text", "text": header_text},
            "body": {"text": text},
            "footer": {"text": footer_text},
            "action": {
                "sections": [section.model_dump() for section in sections],
                "button": button_text,
            },
        },
    }

    url = f"https://graph.facebook.com/v20.0/{Config.BUSINESS_PHONE_ID}/messages"
    headers = {"Authorization": f"Bearer {Config.GRAPH_API_TOKEN}"}
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=message_data)
        response.raise_for_status()


async def send_location_request_message(to_user, text):
    message_data = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "type": "interactive",
        "to": to_user,
        "interactive": {
            "type": "location_request_message",
            "body": {"text": text},
            "action": {"name": "send_location"},
        },
    }

    url = f"https://graph.facebook.com/v20.0/{Config.BUSINESS_PHONE_ID}/messages"
    headers = {"Authorization": f"Bearer {Config.GRAPH_API_TOKEN}"}
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=message_data)
        response.raise_for_status()


async def send_message(business_number, message: Message, response_txt: str):
    message_data = {
        "messaging_product": "whatsapp",
        "to": message.from_user,
        "text": {"body": response_txt},
        "context": {"message_id": message.id},
    }
    url = f"https://graph.facebook.com/v18.0/{business_number}/messages"
    headers = {"Authorization": f"Bearer {Config.GRAPH_API_TOKEN}"}
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=message_data)
        response.raise_for_status()


async def handle_messages(messages: List[Message], metadata: MetaData):
    message = messages[0]
    match message.type:
        case "text":
            await send_to_rapidpro(message.from_user, message.text.body)
        case "reaction":
            pass
        case "image":
            pass
        case "interactive":
            await send_to_rapidpro(message.from_user, message.interactive.list_reply.id)
        case "location":
            await send_to_rapidpro(
                message.from_user,
                f"{message.location.latitude} {message.location.longitude}",
            )
        case "order":
            await send_message(
                metadata.phone_number_id,
                message,
                "Your order has been placed. You will recieve a payment link shortly",
            )
        case _:
            pass
