from functools import lru_cache
from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import model_validator


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')
    environment: Literal['development', 'test', 'production'] = 'development'
    database_url: str = 'sqlite:///./beprogram.db'
    auth_mode: Literal['supabase', 'local'] = 'supabase'
    local_dev_token: str = ''
    supabase_url: str = ''
    supabase_publishable_key: str = ''
    jwt_audience: str = 'authenticated'
    allowed_origins: str = 'http://localhost:5173,http://127.0.0.1:5173'
    app_origin: str = 'http://localhost:8000'
    openai_api_key: str = ''
    openai_model: str = 'gpt-4.1-mini'
    sentry_dsn: str = ''
    elevenlabs_api_key: str = ''
    elevenlabs_voice_id: str = ''
    solana_enabled: bool = False
    solana_rpc_url: str = 'https://api.devnet.solana.com'
    solana_issuer_key: str = ''
    solana_trusted_issuers: str = ''
    composio_api_key: str = ''
    composio_github_auth_config_id: str = ''
    composio_tool_version: str = ''
    operation_timeout: int = 30
    lease_seconds: int = 90

    @model_validator(mode='after')
    def production(self):
        if self.auth_mode == 'local' and (self.environment == 'production' or len(self.local_dev_token) < 32):
            raise ValueError('Local auth requires development mode and a random token of at least 32 characters')
        if self.environment == 'production':
            if not self.supabase_url.startswith('https://') or not self.app_origin.startswith('https://'):
                raise ValueError('Production requires Supabase Auth and an HTTPS app origin')
            if self.database_url.startswith('sqlite'):
                raise ValueError('Production requires PostgreSQL')
        return self


@lru_cache
def settings():
    return Settings()
