import hmac
import jwt
from fastapi import Request
from jwt import PyJWKClient
from .errors import AppError


class Auth:
    def __init__(self, config):
        self.config = config
        self.jwks = PyJWKClient(config.supabase_url.rstrip('/') + '/auth/v1/.well-known/jwks.json', lifespan=300, timeout=5) if config.supabase_url else None

    def __call__(self, request: Request):
        token = request.headers.get('authorization', '')
        if not token.startswith('Bearer '):
            raise AppError('unauthorized', 'Sign in to continue.', 401)
        token = token[7:]
        if self.config.auth_mode == 'local':
            if request.client.host not in ('127.0.0.1', '::1', 'testclient'):
                raise AppError('local_only', 'Development identity is limited to loopback.', 403)
            if hmac.compare_digest(token, self.config.local_dev_token):
                return 'local-developer'
            raise AppError('unauthorized', 'Invalid local development token.', 401)
        if not self.jwks:
            raise AppError('auth_unconfigured', 'Configure Supabase authentication on the server.', 503)
        try:
            key = self.jwks.get_signing_key_from_jwt(token)
            claims = jwt.decode(token, key.key, algorithms=['RS256', 'ES256'], audience=self.config.jwt_audience,
                                issuer=self.config.supabase_url.rstrip('/') + '/auth/v1', options={'require': ['exp', 'iat', 'sub', 'iss', 'aud']})
            if claims.get('role') != 'authenticated' or not claims['sub']:
                raise ValueError('Invalid user role')
            return claims['sub']
        except Exception:
            raise AppError('unauthorized', 'Your session is invalid or expired. Sign in again.', 401) from None
