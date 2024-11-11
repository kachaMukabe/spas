import logging
import yaml
import os
import datetime
import uuid
from fastapi import FastAPI, Response, Request, Depends, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from routers import webhook
from models.models import Order, OrderResponse, RapidProMessage
from models.whatsapp_models import Section
from services import (
    send_interactive_list,
    send_location_request_message,
    send_rapid_message,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


app = FastAPI()

app.include_router(webhook.router)

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./orders.db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=True, bind=engine)
Base = declarative_base()


class PadOrder(Base):
    __tablename__ = "orders"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    phone_number = Column(String, index=True)
    number_of_pads = Column(Integer)
    delivery_address = Column(String)
    special_instructions = Column(String, nullable=True)  # Optional
    status = Column(String, default="Pending")  # Initial status
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Incoming request: {request.method} {request.url}")

    # Optionally, print headers or body
    headers = dict(request.headers)
    logger.info(f"Headers: {headers}")

    body = await request.body()
    logger.info(f"Body: {body.decode('utf-8') if body else 'No body'}")

    # Proceed with the request
    response = await call_next(request)
    return response


@app.post("/callback")
async def handle_rapidpro_callback(payload: RapidProMessage):

    message_data = yaml.safe_load(payload.text)
    logger.info(message_data)

    if type(message_data) is dict:
        if message_data["type"] == "interactive":
            sections = [
                Section.model_validate(section) for section in message_data["sections"]
            ]
            header_text = (
                message_data["header"] if message_data["header"] is not None else ""
            )
            body_text = message_data["body"]
            footer_text = (
                message_data["footer"] if message_data["footer"] is not None else ""
            )
            button_text = message_data["button"]
            await send_interactive_list(
                payload.to,
                header_text,
                message_data["body"],
                footer_text,
                message_data["button"],
                sections,
            )
        elif message_data["type"] == "image":
            pass
        elif message_data["type"] == "catalog":
            pass
            # body_text = message_data["body"]
            # footer_text = message_data["footer"]
            # catalog_id = message_data["catalog"]
            # product_id = message_data["product"]
            # await send_catalog_message(
            #    payload.to, body_text, footer_text, catalog_id, product_id
            # )
        elif message_data["type"] == "location":
            await send_location_request_message(payload.to, message_data["body"])
    else:
        await send_rapid_message(payload.to, message_data)
    return Response("success", status_code=200)


@app.post("/process-order")
async def process_order(order: Order, db: Session = Depends(get_db)):
    logger.info("Herre")
    logger.info(order)
    try:
        db_order = PadOrder(
            phone_number=order.contact.urn,
            number_of_pads=order.results.pads_requested.value,
            delivery_address=order.results.delivery_address.value,
            special_instructions=order.results.special_instructions.value,
        )
        db.add(db_order)
        db.commit()
        db.refresh(db_order)

        response = OrderResponse(status=str(db_order.status), order_id=str(db_order.id))

        return response

    except Exception as e:
        db.rollback()
        print(f"Error processing order: {e}")
        raise HTTPException(status_code=500, detail="Error processing order")
