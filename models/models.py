from pydantic import BaseModel, Field


class RapidProMessage(BaseModel):
    id: str
    to: str
    to_no_plus: str
    from_: str = Field(alias="from")
    from_no_plus: str
    channel: str
    text: str


class Contact(BaseModel):
    name: str
    urn: str
    uuid: str


class Flow(BaseModel):
    name: str
    uuid: str


class Item(BaseModel):
    category: str
    value: str


class Results(BaseModel):
    action: Item
    delivery_address: Item
    pads_requested: Item
    special_instructions: Item


class Order(BaseModel):
    contact: Contact
    flow: Flow
    results: Results


class OrderResponse(BaseModel):
    status: str
    order_id: str
