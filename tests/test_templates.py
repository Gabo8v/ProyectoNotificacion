import uuid

import httpx
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


class TestTemplates:
    def test_list_empty(self, client: TestClient):
        resp = client.get("/templates/")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_create_template(self, client: TestClient):
        resp = client.post("/templates/", json={
            "name": "saludo",
            "keywords": "hola,buenas",
            "subject": "Saludo",
            "body": "Hola, como estas?",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "saludo"
        assert data["keywords"] == "hola,buenas"
        assert data["is_active"] is True

    def test_create_duplicate_name(self, client: TestClient):
        import httpx
        client.post("/templates/", json={
            "name": "dup_test",
            "keywords": "test",
            "body": "Cuerpo",
        })
        with pytest.raises((httpx.HTTPError, Exception)):
            client.post("/templates/", json={
                "name": "dup_test",
                "keywords": "test",
                "body": "Cuerpo",
            })

    def test_list_templates(self, client: TestClient):
        client.post("/templates/", json={
            "name": "consulta",
            "keywords": "consulta,precio",
            "body": "Gracias por tu consulta",
        })
        resp = client.get("/templates/")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) >= 1
        names = [t["name"] for t in data]
        assert "consulta" in names

    def test_delete_template(self, client: TestClient, db: Session):
        from app.models.template import Template
        tpl = Template(name="temp", keywords="del", body="Para borrar")
        db.add(tpl)
        db.commit()
        tpl_id = str(tpl.id)

        resp = client.delete(f"/templates/{tpl_id}")
        assert resp.status_code == 200
        assert resp.json() == {"ok": True}

        assert db.query(Template).filter(Template.id == tpl_id).first() is None
