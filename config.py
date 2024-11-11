import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
    GRAPH_API_TOKEN = os.getenv("GRAPH_API_TOKEN")
    RAPID_PRO_URL = os.getenv("RAPID_PRO_URL")
    BUSINESS_PHONE_ID = os.getenv("BUSINESS_PHONE_ID")
