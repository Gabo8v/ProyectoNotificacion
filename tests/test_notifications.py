from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


class TestNotifications:
    def test_send_email_notification(self, client: TestClient, create_user):
        user_id = str(create_user.id)
        resp = client.post("/notifications/send", json={
            "user_id": user_id,
            "channel": "email",
            "subject": "Test asunto",
            "body": "Test cuerpo del mensaje",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["channel"] == "email"
        assert data["status"] == "pending"
        assert data["subject"] == "Test asunto"
        assert data["body"] == "Test cuerpo del mensaje"
        assert data["user_id"] == user_id

    def test_send_whatsapp_notification(self, client: TestClient, create_user):
        resp = client.post("/notifications/send", json={
            "user_id": str(create_user.id),
            "channel": "whatsapp",
            "body": "Mensaje de WhatsApp",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["channel"] == "whatsapp"
        assert data["status"] == "pending"

    def test_send_without_user(self, client: TestClient):
        resp = client.post("/notifications/send", json={
            "channel": "email",
            "subject": "Sin usuario",
            "body": "Notificacion sin user_id",
        })
        assert resp.status_code == 200
        assert resp.json()["user_id"] is None

    def test_history_empty(self, client: TestClient):
        resp = client.get("/notifications/history")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_history_with_filters(self, client: TestClient, create_user):
        client.post("/notifications/send", json={
            "user_id": str(create_user.id),
            "channel": "email",
            "subject": "Filtro test",
            "body": "Cuerpo",
        })
        resp = client.get("/notifications/history?channel=email&status=pending")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) >= 1
        for n in data:
            assert n["channel"] == "email"
            assert n["status"] == "pending"

    def test_history_limit_offset(self, client: TestClient, create_user):
        for i in range(5):
            client.post("/notifications/send", json={
                "user_id": str(create_user.id),
                "channel": "email",
                "subject": f"Notif {i}",
                "body": f"Cuerpo {i}",
            })
        resp = client.get("/notifications/history?limit=2&offset=0")
        data = resp.json()
        assert len(data) <= 2
