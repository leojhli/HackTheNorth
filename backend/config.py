from functools import lru_cache
from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import model_validator
from urllib.parse import urlsplit


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
    ollama_url: str = 'http://127.0.0.1:11435'
    ollama_model: Literal['qwen2.5-coder:7b', 'qwen2.5-coder:3b', 'qwen3:4b-instruct-2507-q4_K_M', 'qwen3.5:4b'] = 'qwen2.5-coder:7b'
    ollama_context: int = 16384
    local_logs_enabled: bool = True
    local_log_path: str = '.tools/logs/lifecycle.jsonl'
    sentry_dsn: str = ''
    sentry_enabled: bool = False
    elevenlabs_api_key: str = ''
    elevenlabs_voice_id: str = ''
    solana_enabled: bool = False
    solana_rpc_url: str = 'https://api.devnet.solana.com'
    solana_issuer_key: str = ''
    solana_trusted_issuers: str = ''
    composio_api_key: str = ''
    composio_github_auth_config_id: str = ''
    composio_tool_version: str = ''
    operation_timeout: int = 120
    lease_seconds: int = 180

    @model_validator(mode='after')
    def production(self):
        if self.sentry_enabled:
            from sentry_sdk.utils import Dsn
            try:
                dsn = Dsn(self.sentry_dsn)
                if dsn.scheme != 'https' or not dsn.host.endswith('.ingest.sentry.io') and not dsn.host.endswith('.ingest.us.sentry.io') and not dsn.host.endswith('.ingest.de.sentry.io'):
                    raise ValueError()
            except Exception:
                raise ValueError('Enabled Sentry requires an HTTPS project DSN from Sentry; leave it disabled until configured.') from None
        endpoint = urlsplit(self.ollama_url)
        if (endpoint.scheme != 'http' or endpoint.hostname not in {'127.0.0.1', '::1'}
                or endpoint.username or endpoint.password or endpoint.query or endpoint.fragment
                or endpoint.path not in {'', '/'}):
            raise ValueError('Ollama must use a literal loopback HTTP address; cloud endpoints are disabled')
        if not 4096 <= self.ollama_context <= 32768:
            raise ValueError('Local model context must be between 4096 and 32768 tokens')
        if not 10 <= self.operation_timeout <= 120 or self.lease_seconds < self.operation_timeout + 30:
            raise ValueError('Local operation timeout must be 10-120 seconds and lease must allow 30 seconds extra')
        if self.solana_rpc_url != 'https://api.devnet.solana.com':
            raise ValueError('Only the public free Solana Devnet RPC is supported')
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
