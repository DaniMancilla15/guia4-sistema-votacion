import pytest
from datetime import datetime, timedelta

from app import create_app
from models import db, Eleccion, Candidato

@pytest.fixture
def app():
    app = create_app({
        "TESTING": True,
        "SECRET_KEY": "test",
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"
    })

    with app.app_context():
        db.create_all()
        eleccion = Eleccion(
            nombre="Elección de prueba",
            descripcion="Prueba",
            fecha_inicio=datetime.utcnow() - timedelta(hours=1),
            fecha_fin=datetime.utcnow() + timedelta(hours=1),
            activa=True
        )
        db.session.add(eleccion)
        db.session.flush()
        db.session.add_all([
            Candidato(eleccion_id=eleccion.id, nombre="Candidato A"),
            Candidato(eleccion_id=eleccion.id, nombre="Candidato B")
        ])
        db.session.commit()

    yield app

@pytest.fixture
def client(app):
    return app.test_client()

def registrar_y_loguear(client, correo="daniela@example.com"):
    r = client.post("/register", json={
        "nombre": "Daniela",
        "correo": correo,
        "password": "123456"
    })
    assert r.status_code == 201

    r = client.post("/login", json={
        "correo": correo,
        "password": "123456"
    })
    assert r.status_code == 200

def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.get_json()["status"] == "ok"

def test_registro_login_y_listado(client):
    registrar_y_loguear(client)
    r = client.get("/elecciones")
    assert r.status_code == 200
    assert len(r.get_json()) == 1

def test_voto_unico_por_eleccion(client):
    registrar_y_loguear(client)

    r = client.post("/vote", json={"eleccion_id": 1, "candidato_id": 1})
    assert r.status_code == 201

    r = client.post("/vote", json={"eleccion_id": 1, "candidato_id": 2})
    assert r.status_code == 409

def test_resultados(client):
    registrar_y_loguear(client)
    client.post("/vote", json={"eleccion_id": 1, "candidato_id": 1})

    r = client.get("/results/1")
    assert r.status_code == 200
    data = r.get_json()
    assert data["eleccion"] == "Elección de prueba"
    assert sum(x["votos"] for x in data["resultados"]) == 1
