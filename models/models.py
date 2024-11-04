from pydantic import BaseModel, Field


class RapidProMessage(BaseModel):
    id: str
    to: str
    to_no_plus: str
    from_: str = Field(alias="from")
    from_no_plus: str
    channel: str
    text: str
