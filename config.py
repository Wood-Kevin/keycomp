import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev")
    RAIDERIO_BASE_URL = os.getenv("RAIDERIO_BASE_URL", "https://raider.io/api/v1")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
