"""Run: python -m unittest backend.test_shared_auth"""
import unittest

from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route
from starlette.testclient import TestClient

from backend.shared_auth import SharedPasswordMiddleware

PASSWORD = 'local-test-password-2026'


class SharedAuthenticationTests(unittest.TestCase):
    def make_client(self, password=PASSWORD, external_scheme=None):
        self.calls = 0

        async def endpoint(request):
            self.calls += 1
            return JSONResponse({'ok': True})

        app = Starlette(routes=[Route('/{path:path}', endpoint, methods=['GET', 'POST'])])
        app.add_middleware(SharedPasswordMiddleware, username='guest', password=password, external_scheme=external_scheme)
        return TestClient(app)

    def test_all_private_routes_require_authentication(self):
        with self.make_client() as client:
            for path in ('/', '/assets/app.js', '/docs', '/openapi.json', '/api/chat'):
                response = client.request('POST' if path == '/api/chat' else 'GET', path)
                self.assertEqual(response.status_code, 401)
                self.assertIn('Basic', response.headers['www-authenticate'])
            self.assertEqual(self.calls, 0)

    def test_wrong_and_malformed_credentials_are_rejected(self):
        with self.make_client() as client:
            self.assertEqual(client.get('/', auth=('guest', 'wrong')).status_code, 401)
            self.assertEqual(client.get('/', auth=('wrong', PASSWORD)).status_code, 401)
            self.assertEqual(client.get('/', headers={'Authorization': 'Basic ???'}).status_code, 401)
            self.assertEqual(self.calls, 0)

    def test_valid_credentials_and_same_origin_post(self):
        with self.make_client() as client:
            response = client.get('/', auth=('guest', PASSWORD))
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.headers['cache-control'], 'no-store')
            self.assertEqual(client.post('/api/chat', auth=('guest', PASSWORD), headers={'Origin': 'http://testserver'}).status_code, 200)

    def test_missing_or_short_secret_fails_closed_except_health(self):
        for password in ('', 'short'):
            with self.make_client(password) as client:
                self.assertEqual(client.get('/api/health').status_code, 200)
                self.assertEqual(client.get('/').status_code, 503)
                self.assertEqual(client.post('/api/chat').status_code, 503)

    def test_cloud_run_tls_termination(self):
        # The ASGI request is HTTP, while the actual browser origin is HTTPS.
        with self.make_client(external_scheme='https') as client:
            self.assertEqual(client.post('/api/chat', auth=('guest', PASSWORD), headers={'Origin': 'https://testserver', 'Sec-Fetch-Site': 'same-origin'}).status_code, 200)
            for origin in ('http://testserver', 'https://other.example', 'https://testserver.evil.example'):
                self.assertEqual(client.post('/api/chat', auth=('guest', PASSWORD), headers={'Origin': origin}).status_code, 403)
            self.assertEqual(self.calls, 1)

    def test_other_sites_cannot_trigger_api_calls(self):
        with self.make_client() as client:
            self.assertEqual(client.post('/api/chat', auth=('guest', PASSWORD), headers={'Origin': 'https://other.example'}).status_code, 403)
            self.assertEqual(client.post('/api/chat', auth=('guest', PASSWORD), headers={'Sec-Fetch-Site': 'cross-site'}).status_code, 403)
            self.assertEqual(self.calls, 0)


if __name__ == '__main__':
    unittest.main()
