"""Shared browser authentication for the public API and static frontend."""
import base64
import binascii
import hashlib
import secrets

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse


class SharedPasswordMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, *, username: str, password: str, external_scheme: str | None = None):
        super().__init__(app)
        self.username = username.encode('utf-8')
        self.password = password.encode('utf-8')
        self.external_scheme = external_scheme

    async def dispatch(self, request, call_next):
        # Cloud Run health probes do not carry browser credentials.
        if request.url.path == '/api/health' and request.method in ('GET', 'HEAD'):
            return await call_next(request)

        # A missing secret must never silently make the application public.
        if len(self.password) < 16 or not self.username:
            return JSONResponse({'detail': '共有認証が設定されていません。管理者に連絡してください。'}, status_code=503)

        authenticated = False
        header = request.headers.get('authorization', '')
        scheme, _, token = header.partition(' ')
        if scheme.lower() == 'basic' and len(token) <= 8192:
            try:
                decoded = base64.b64decode(token, validate=True)
                username, separator, password = decoded.partition(b':')
                user_ok = secrets.compare_digest(hashlib.sha256(username).digest(), hashlib.sha256(self.username).digest())
                password_ok = secrets.compare_digest(hashlib.sha256(password).digest(), hashlib.sha256(self.password).digest())
                authenticated = bool(separator) and user_ok and password_ok
            except (ValueError, binascii.Error):
                pass
        if not authenticated:
            return JSONResponse(
                {'detail': 'ユーザー名とパスワードを入力してください。'},
                status_code=401,
                headers={'WWW-Authenticate': 'Basic realm="GitLearn", charset="UTF-8"', 'Cache-Control': 'no-store'},
            )

        if request.method not in ('GET', 'HEAD', 'OPTIONS'):
            # Browsers automatically reuse Basic credentials. Reject requests
            # initiated from other sites before they can trigger paid work.
            origin = request.headers.get('origin')
            # Cloud Run terminates TLS before forwarding HTTP to the container.
            # K_SERVICE is checked by the caller, rather than trusting a
            # client-supplied forwarding header to select the public scheme.
            base_url = request.base_url
            if self.external_scheme:
                base_url = base_url.replace(scheme=self.external_scheme)
            expected_origin = str(base_url).rstrip('/')
            if request.headers.get('sec-fetch-site') == 'cross-site' or (origin and origin != expected_origin):
                return JSONResponse({'detail': '別のサイトからの送信は許可されていません。'}, status_code=403)
        response = await call_next(request)
        response.headers['Cache-Control'] = 'no-store'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['Referrer-Policy'] = 'same-origin'
        response.headers['X-Frame-Options'] = 'DENY'
        return response
