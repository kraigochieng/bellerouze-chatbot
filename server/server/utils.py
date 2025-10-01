import json
from datetime import datetime
import requests
import httpx
from langchain_core.messages import HumanMessage, SystemMessage

from server.llm import llm
from server.logger import logger
from server.prompt import SYSTEM_PROMPT
from server.schemas import IncomingMessage, ReplyMessage, StatusUpdate
from server.settings import settings


async def generate_reply(user_message: str) -> str:
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=user_message),
    ]
    response = await llm.ainvoke(messages)
    return response.content


def get_text_message_input(recipient: str, text: str) -> str:
    return json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": recipient,
            "type": "text",
            "text": {"preview_url": False, "body": text},
        }
    )


# def parse_whatsapp_webhook(data: dict) -> IncomingMessage | StatusUpdate | None:
#     """
#     Extracts useful info from WhatsApp webhook payload.
#     Returns a dictionary for flexibility.
#     """
#     try:
#         entry = data["entry"][0]
#         # 746599524843368
#         message_id = entry["id"]

#         changes = entry["changes"][0]
#         value = changes["value"]
#         metadata = value["metadata"]
#         api_phone_number = metadata["display_phone_number"]
#         api_phone_number_id = metadata["phone_number_id"]

#         if "messages" in value:
#             contact = value["contacts"][0]
#             contact_profile_name = contact["profile"]["name"]
#             sender_contact_number = contact["wa_id"]

#             message = value["messages"][0]
#             message_type = message["type"]

#             timestamp = datetime.fromtimestamp(float(message["timestamp"]))

#             if message_type == "text":
#                 from_number = message["from"]
#                 message_body = message["text"]["body"]

#                 return IncomingMessage(
#                     type="message",
#                     timestamp=timestamp.strftime("%d/%m/%YT%H:%M:%S"),
#                     phone_number_id=api_phone_number_id,
#                     from_number=from_number,
#                     incoming_message=message_body,
#                 )
#             else:
#                 return None

#         if "statuses" in value:
#             status = value["statuses"][0]
#             status_id = status["id"]
#             status_value = status["status"]

#             timestamp = datetime.fromtimestamp(float(status["timestamp"]))

#             return StatusUpdate(
#                 type="status",
#                 timestamp=timestamp.strftime("%d/%m/%YT%H:%M:%S"),
#                 phone_number_id=api_phone_number,
#                 status=status_value,
#                 message_id=status_id,
#                 recipient_id=status["recipient_id"],
#             )
#     except Exception as e:
#         logger.exception(str(e))

#         return None


def parse_whatsapp_webhook(data: dict) -> IncomingMessage | StatusUpdate | None:
    """
    Extracts useful info from WhatsApp webhook payload.
    Returns a dictionary for flexibility.
    """
    try:
        entry = data["entry"][0]
        changes = entry["changes"][0]
        value = changes["value"]

        if "messages" in value:
            return parse_incoming_message(data)

        if "statuses" in value:
            return parse_status(data)
    except Exception as e:
        logger.exception(str(e))

        return None


def parse_reply_message(raw: dict, reply_text: str = "placeholder") -> ReplyMessage:
    message = raw["messages"][0]
    message_id = message["id"]

    contact = raw["contacts"][0]
    to_number = contact["wa_id"]

    return ReplyMessage(to_number=to_number, message_id=message_id, message=reply_text)


# def parse_message(raw: dict) -> dict:
#     input = raw["input"]
#     output = raw["output"]
#     reply_text = raw["reply_text"]

#     parsed_input: IncomingMessage = parse_incoming_message(input)
#     parsed_output: ReplyMessage = parse_whatsapp_reply(output, reply_text)


#     return {"input": parsed_input.model_dump(), "output": parsed_output.model_dump()}


def parse_incoming_message(data: dict) -> IncomingMessage | None:
    try:
        entry = data["entry"][0]

        message_id = entry["id"]

        changes = entry["changes"][0]
        value = changes["value"]
        metadata = value["metadata"]
        api_phone_number = metadata["display_phone_number"]
        api_phone_number_id = metadata["phone_number_id"]

        contact = value["contacts"][0]
        contact_profile_name = contact["profile"]["name"]
        sender_contact_number = contact["wa_id"]

        message = value["messages"][0]
        message_type = message["type"]

        # timestamp = datetime.fromtimestamp(float(message["timestamp"]))
        timestamp = message["timestamp"]

        if message_type == "text":
            from_number = message["from"]
            message_body = message["text"]["body"]

            return IncomingMessage(
                type="message",
                # timestamp=timestamp.strftime("%d/%m/%YT%H:%M:%S"),
                timestamp=timestamp,
                phone_number_id=api_phone_number_id,
                from_number=from_number,
                incoming_message=message_body,
            )
        else:
            return None

    except Exception as e:
        logger.exception(str(e))

        return None


def parse_status(data: dict) -> StatusUpdate | None:
    try:
        entry = data["entry"][0]
        # 746599524843368

        changes = entry["changes"][0]
        value = changes["value"]
        metadata = value["metadata"]
        api_phone_number = metadata["display_phone_number"]
        api_phone_number_id = metadata["phone_number_id"]

        status = value["statuses"][0]
        status_id = status["id"]
        status_value = status["status"]

        # timestamp = datetime.fromtimestamp(float(status["timestamp"]))
        timestamp = status["timestamp"]

        return StatusUpdate(
            type="status",
            # timestamp=timestamp.strftime("%d/%m/%YT%H:%M:%S"),
            timestamp=timestamp,
            phone_number_id=api_phone_number,
            status=status_value,
            message_id=status_id,
            recipient_id=status["recipient_id"],
        )
    except Exception as e:
        logger.exception(str(e))

        return None


def build_reply_message(to: str, text: str) -> dict:
    """
    Build WhatsApp API reply payload.
    """
    return {
        "messaging_product": "whatsapp",
        "to": to,
        "text": {"body": text},
    }


async def send_whatsapp_message(phone_number_id: str, payload: dict) -> httpx.Response:
    """
    Sends a WhatsApp message via Graph API.
    Returns the raw httpx.Response object.
    """
    url = f"https://graph.facebook.com/{settings.whatsapp_api_version}/{phone_number_id}/messages"
    headers = {
        "Authorization": f"Bearer {settings.whatsapp_access_token}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(url, headers=headers, json=payload)
        print(f"📨 Sent to {url} with status {response.status_code}")
        return response


def ping_self():
    try:
        requests.get(settings.server_url, timeout=5)
        print("Pinged self ✅")
    except Exception as e:
        print("Ping failed ❌", e)
