from dotenv import load_dotenv
import os

load_dotenv()


class Config:
    BINANCE_API_KEY = os.getenv("BINANCE_API_KEY", '')
    BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET", '')
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", '')
    DATABASE_URL = os.getenv("POSTGRES_URL", '')
