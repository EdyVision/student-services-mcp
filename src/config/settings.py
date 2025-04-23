from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class CommonSettings(BaseSettings):
    APP_NAME: str = "Student Services Demo MCP"
    APP_VERSION: str = "0.1.0"
    APP_DESCRIPTION: str = "A demo MCP for a fictitious university"
    DEBUG_MODE: bool = False


class HuggingFaceSettings(BaseSettings):
    HUGGINGFACE_TOKEN: str = ""
    HUGGINGFACE_SPACE_URL: str = ""


class ServerSettings(BaseSettings):
    HOST: str = "0.0.0.0"
    PORT: int = 7860


class AuthSettings(BaseSettings):
    AUTH_ENABLED: bool = True
    AUTH_TOKEN: str = ""


class Settings:
    def __init__(self):
        self.common = CommonSettings()
        self.hf = HuggingFaceSettings()
        self.server = ServerSettings()
        self.auth = AuthSettings()


settings = Settings()
