import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", 5433))
DB_NAME = os.getenv("DB_NAME", "sovkombank")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "Demon913133")

CHECK_API_TOKEN = "32618.OHg47TOLhPU2MFE9k"



JWT_SECRET = os.getenv("JWT_SECRET", "inSeregaveritas")
JWT_ALGORITHM = "HS256"
