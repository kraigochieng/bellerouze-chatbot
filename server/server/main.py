import json
from contextlib import asynccontextmanager
from math import ceil
from typing import List, Literal

import pymongo
import uvicorn
from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI, HTTPException, Query, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pymongo import MongoClient

from server.logger import logger
from server.schemas import MessageWithStatusResponse, PaginatedResponse
from server.settings import settings
from server.utils import (
    build_reply_message,
    generate_reply,
    parse_incoming_message,
    parse_reply_message,
    parse_status,
    parse_whatsapp_webhook,
    ping_self,
    send_whatsapp_message,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start scheduler
    scheduler = BackgroundScheduler()
    scheduler.add_job(ping_self, "interval", minutes=5)  # every 10 min
    scheduler.start()
    logger.info("Scheduler started")

    yield

    scheduler.shutdown()
    logger.info("Scheduler stopped")


app = FastAPI(lifespan=lifespan)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.client_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def index():
    return {"message": "juu"}


@app.get("/webhook")
async def verify_webhook(request: Request):
    """
    WhatsApp webhook verification (GET).
    Facebook will send hub.challenge here.
    """
    params = request.query_params
    if (
        params.get("hub.mode") == "subscribe"
        and params.get("hub.verify_token") == settings.whatsapp_verify_token
    ):
        return JSONResponse(content=int(params.get("hub.challenge")))
    return JSONResponse(content={"error": "Invalid verification"}, status_code=403)


@app.post("/webhook")
async def receive_webhook(request: Request):
    """
    Handles WhatsApp messages (POST).
    """

    data = await request.json()

    logger.info("🔔 Webhook received: {}", data)
    # logger.info("🔔 Webhook received:\n{}", json.dumps(data, indent=2))

    try:
        mongo_client = MongoClient(settings.mongo_uri)

        database = mongo_client.get_database("bellerouze_chatbot")

        logger.debug("Inserted message into MongoDB")

        parsed = parse_whatsapp_webhook(data)

        if not parsed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Message not parsed"
            )

        if parsed.type == "message":
            reply_text = await generate_reply(parsed.incoming_message)
            payload = build_reply_message(to=parsed.from_number, text=reply_text)

            response = await send_whatsapp_message(parsed.phone_number_id, payload)

            if response.headers.get("content-type", "").startswith("application/json"):
                # logger.info(
                #     "✅ Reply response:\n{}", json.dumps(response.json(), indent=2)
                # )
                logger.info("✅ Reply response: {}", response.json())
            else:
                logger.warning("⚠️ Raw response: {}", response.text)

            messages_collection = database.get_collection("messages")
            messages_collection.insert_one(
                {
                    "input": data,
                    "output": response.json(),
                    "reply_text": reply_text,
                    "version": settings.whatsapp_api_version,
                }
            )

        elif parsed.type == "status":
            statuses_collection = database.get_collection("statuses")
            statuses_collection.insert_one(data)

            logger.info(
                "ℹ️ Status update for message {}: {}",
                parsed.message_id,
                parsed.status,
            )

        else:
            logger.warning("⚠️ Unknown webhook type: {}", parsed.type)

        mongo_client.close()

    except Exception as e:
        logger.exception(f"❌ Error processing webhook: {str(e)}")

    return JSONResponse(content={"status": "received"})


@app.get("/messages", response_model=PaginatedResponse[MessageWithStatusResponse])
async def get_messages_with_statuses(
    phone_number: str | None = Query(
        default=None, description="The phone number without the  e.g 254712345678"
    ),
    page: int = Query(1, ge=0, description="Number of records to skip"),
    size: int = Query(20, ge=1, le=100, description="Max number of records to return"),
    sort_field: str = Query(
        "input.entry.0.changes.0.value.messages.0.timestamp",
        description="Field to sort by",
    ),
    sort_order: Literal["asc", "desc"] = Query(
        "desc", description="Sort order: 'asc' or 'desc'"
    ),
    search: str | None = Query(
        default=None, description="Search text (matches phone or message content)"
    ),
):
    try:
        mongo_client = MongoClient(settings.mongo_uri)
        database = mongo_client.get_database("bellerouze_chatbot")
        collection = database.get_collection("messages")

        parsed = []

        base_filter = {}

        if phone_number:
            base_filter["input.entry.0.changes.0.value.contacts.0.wa_id"] = phone_number

        if search:
            base_filter["$or"] = [
                {
                    "input.entry.0.changes.0.value.contacts.0.wa_id": {
                        "$regex": search,
                        "$options": "i",
                    }
                },
                {
                    "input.entry.0.changes.0.value.messages.0.text.body": {
                        "$regex": search,
                        "$options": "i",
                    }
                },
                {"reply_text": {"$regex": search, "$options": "i"}},
            ]

        total = collection.count_documents(base_filter)

        skip = (page - 1) * size
        pages = ceil(total / size) if total > 0 else 1

        pymongo_sort_order = (
            pymongo.ASCENDING if sort_order == "asc" else pymongo.DESCENDING
        )

        pipeline = []

        if phone_number:
            pipeline.append(
                {
                    "$match": {
                        "input.entry.0.changes.0.value.contacts.0.wa_id": phone_number
                    }
                }
            )

        pipeline.extend(
            [
                {
                    "$lookup": {
                        "from": "statuses",
                        "localField": "output.messages.id",
                        "foreignField": "entry.changes.value.statuses.id",
                        "as": "statuses",
                    }
                },
                {"$sort": {sort_field: pymongo_sort_order}},
                {"$skip": skip},
                {"$limit": size},
            ]
        )

        raw_docs = collection.aggregate(pipeline)

        for raw in raw_docs:
            input = raw["input"]
            output = raw["output"]
            reply_text = raw["reply_text"]
            statuses = raw["statuses"]

            parsed_input = parse_incoming_message(input)
            parsed_output = parse_reply_message(output, reply_text)

            parsed_statuses = []
            for status_item in statuses:
                parsed_status = parse_status(status_item)
                parsed_statuses.append(parsed_status)

            parsed.append(
                {
                    "incoming_message": parsed_input,
                    "reply_message": parsed_output,
                    "statuses": parsed_statuses,
                }
            )

        mongo_client.close()

        response = {
            "items": parsed,
            "total": total,
            "page": page,
            "size": size,
            "pages": pages,
        }

        return JSONResponse(content=jsonable_encoder(response))

    except Exception as e:
        return JSONResponse(
            content={"error": f"Failed to fetch messages: {str(e)}"},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


if __name__ == "__main__":
    uvicorn.run(
        "server.main:app",  # Your FastAPI app
        host="0.0.0.0",
        port=8000,
        log_config=None,
        log_level=None,
        reload=True,
    )
