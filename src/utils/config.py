from pathlib import Path

from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

ROOT_DIR = str(Path(__file__).parent.parent.parent)

class AppSettings(BaseSettings):

    GOOGLE_API_KEY: str | None
    EMBEDDING_MODEL_NAME: str | None
    JD_EMBEDDING_FILE_NAME: str | None
    RESUME_EMBEDDING_FILE_NAME: str | None

    class Config:
        env_file = f'{ROOT_DIR}/.env'

settings = AppSettings()