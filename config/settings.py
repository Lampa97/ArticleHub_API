import os

from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
DB_URL = os.getenv("DB_URL")
DB_NAME = os.getenv("DB_NAME")
LOGS_DIR = os.path.join(os.getcwd(), "logs")
