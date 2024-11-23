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
from models.models import (
    Order,
    OrderIDRequest,
    OrderResponse,
    PhoneNumberRequest,
    RapidProMessage,
)
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

    try:
        message_data = yaml.safe_load(payload.text)
        logger.info(message_data)
    except Exception as e:
        logger.error(f"Error parsing message data: {e}")
        message_data = payload.text

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
            phone_number=order.contact.urn.replace("tel:", ""),
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


@app.post("/orders")
async def get_orders_by_phone_number(
    request: PhoneNumberRequest, db: Session = Depends(get_db)
):
    try:
        phone_number = request.phone_number
        orders = db.query(PadOrder).filter(PadOrder.phone_number == phone_number).all()

        if not orders:
            raise HTTPException(
                status_code=404, detail="No orders found for this phone number"
            )

        # Extract order IDs
        order_ids = [
            str(order.id) for order in orders
        ]  # Convert UUID to string if needed
        logger.info(order_ids)

        return {"order_ids": order_ids}

    except HTTPException as e:  # Re-raise HTTPExceptions
        raise e

    except Exception as e:  # Handle other database errors
        print(f"Error retrieving orders: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving orders")


@app.post("/order")
async def get_order_by_id(
    request: OrderIDRequest, db: Session = Depends(get_db)
):  # order_id is a string (or UUID if applicable)

    try:

        order_id = request.order_id
        order = db.query(PadOrder).filter(PadOrder.id == order_id).first()

        if not order:
            raise HTTPException(status_code=404, detail="Order not found")

        # Convert the SQLAlchemy object to a dictionary (or Pydantic model if you prefer)
        order_data = (
            order.__dict__
        )  #  Excludes private attributes (those starting with '_')

        # If Order.id is a UUID, convert it to a string in the response:
        if isinstance(order.id, uuid.UUID):
            order_data["id"] = str(order.id)

        return order_data

    except HTTPException as e:  # Re-raise the HTTPException
        raise e

    except (
        Exception
    ) as e:  # Catch any other potential errors (e.g., database errors during UUID conversion)
        print(f"Error retrieving order: {e}")  # Log the error for debugging
        raise HTTPException(status_code=500, detail="Error retrieving order")
