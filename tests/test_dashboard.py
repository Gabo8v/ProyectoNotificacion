from fastapi.testclient import TestClient


class TestDashboard:
    def test_index(self, client: TestClient):
        resp = client.get("/dashboard/")
        assert resp.status_code == 200
        assert "Resumen" in resp.text
        assert "Total" in resp.text

    def test_send_form(self, client: TestClient):
        resp = client.get("/dashboard/send")
        assert resp.status_code == 200
        assert "Enviar" in resp.text

    def test_templates_page(self, client: TestClient):
        resp = client.get("/dashboard/templates")
        assert resp.status_code == 200
        assert "Templates" in resp.text

    def test_history_page(self, client: TestClient):
        resp = client.get("/dashboard/history")
        assert resp.status_code == 200
        assert "Historial" in resp.text
