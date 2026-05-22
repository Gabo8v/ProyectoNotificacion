from fastapi.testclient import TestClient


class TestWhatsApp:
    def test_webhook_received(self, client: TestClient):
        resp = client.post("/whatsapp/webhook", json={
            "from": "5493875360385@c.us",
            "body": "Hola, esto es una prueba",
            "messageId": "test_msg_id_001",
            "timestamp": 1700000000,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "received"
        assert data["from"] == "5493875360385@c.us"
        assert data["body"] == "Hola, esto es una prueba"
