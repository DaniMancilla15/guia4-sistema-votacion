from datetime import datetime
from flask import Flask, jsonify, request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from config import Config
from models import db, Usuario, Eleccion, Candidato, Voto

login_manager = LoginManager()

def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_object(Config)

    if test_config:
        app.config.update(test_config)

    db.init_app(app)
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(Usuario, int(user_id))

    @app.get("/health")
    def health():
        return jsonify({"status": "ok"}), 200

    @app.post("/register")
    def register():
        data = request.get_json() or {}
        nombre = (data.get("nombre") or "").strip()
        correo = (data.get("correo") or "").strip().lower()
        password = data.get("password") or ""

        if not nombre or not correo or len(password) < 6:
            return jsonify({"error": "Datos inválidos. La contraseña debe tener mínimo 6 caracteres."}), 400

        if Usuario.query.filter_by(correo=correo).first():
            return jsonify({"error": "El correo ya está registrado."}), 409

        usuario = Usuario(
            nombre=nombre,
            correo=correo,
            password_hash=generate_password_hash(password)
        )
        db.session.add(usuario)
        db.session.commit()
        return jsonify({"mensaje": "Usuario registrado.", "id": usuario.id}), 201

    @app.post("/login")
    def login():
        data = request.get_json() or {}
        correo = (data.get("correo") or "").strip().lower()
        password = data.get("password") or ""

        usuario = Usuario.query.filter_by(correo=correo, activo=True).first()
        if not usuario or not check_password_hash(usuario.password_hash, password):
            return jsonify({"error": "Credenciales inválidas."}), 401

        login_user(usuario)
        return jsonify({"mensaje": "Inicio de sesión correcto.", "usuario": usuario.nombre}), 200

    @app.post("/logout")
    @login_required
    def logout():
        logout_user()
        return jsonify({"mensaje": "Sesión cerrada."}), 200

    @app.get("/elecciones")
    @login_required
    def elecciones():
        items = Eleccion.query.order_by(Eleccion.fecha_inicio.asc()).all()
        return jsonify([
            {
                "id": e.id,
                "nombre": e.nombre,
                "descripcion": e.descripcion,
                "fecha_inicio": e.fecha_inicio.isoformat(),
                "fecha_fin": e.fecha_fin.isoformat(),
                "activa": e.activa,
                "candidatos": [{"id": c.id, "nombre": c.nombre} for c in e.candidatos],
            }
            for e in items
        ])

    @app.post("/vote")
    @login_required
    def vote():
        data = request.get_json() or {}
        eleccion_id = data.get("eleccion_id")
        candidato_id = data.get("candidato_id")

        eleccion = db.session.get(Eleccion, eleccion_id)
        candidato = db.session.get(Candidato, candidato_id)

        if not eleccion or not candidato or candidato.eleccion_id != eleccion.id:
            return jsonify({"error": "Elección o candidato inválido."}), 400

        ahora = datetime.utcnow()
        if not eleccion.activa or ahora < eleccion.fecha_inicio or ahora > eleccion.fecha_fin:
            return jsonify({"error": "La elección no está disponible."}), 400

        existente = Voto.query.filter_by(
            usuario_id=current_user.id,
            eleccion_id=eleccion.id
        ).first()
        if existente:
            return jsonify({"error": "El usuario ya votó en esta elección."}), 409

        voto = Voto(
            usuario_id=current_user.id,
            eleccion_id=eleccion.id,
            candidato_id=candidato.id
        )
        db.session.add(voto)
        db.session.commit()
        return jsonify({"mensaje": "Voto registrado correctamente."}), 201

    @app.get("/results/<int:eleccion_id>")
    @login_required
    def results(eleccion_id):
        eleccion = db.session.get(Eleccion, eleccion_id)
        if not eleccion:
            return jsonify({"error": "Elección no encontrada."}), 404

        resultados = []
        for candidato in eleccion.candidatos:
            total = Voto.query.filter_by(candidato_id=candidato.id).count()
            resultados.append({"candidato": candidato.nombre, "votos": total})

        return jsonify({"eleccion": eleccion.nombre, "resultados": resultados}), 200

    return app

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(debug=True)
