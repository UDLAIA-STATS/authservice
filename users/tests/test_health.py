import json
from users.tests.config import Usuario, UsuarioAPITestCase


class HealthTestCase(UsuarioAPITestCase):
    def test_health_endpoint_returns_json_with_status_ok(self):
        """✅ El endpoint /health/ retorna JSON con status ok"""
        response = self.client.get("/api/health/")
        payload = json.loads(response.content.decode('utf-8'))
        self.assertEqual(payload['data'], {"status": "ok"})

    def test_health_endpoint_returns_200(self):
        """✅ El endpoint /health/ retorna 200 OK"""
        response = self.client.get("/api/health/")
        self.assertEqual(response.status_code, 200)

    def test_health_endpoint_allows_access_without_authentication(self):
        """✅ El endpoint /health/ permite acceso sin autenticación"""
        # No autenticamos al cliente
        response = self.client.get("/api/health/")
        self.assertEqual(response.status_code, 200)
        content_string = response.content.decode('utf-8')
        data = json.loads(content_string)
        self.assertEqual(data['data'], {"status": "ok"})

