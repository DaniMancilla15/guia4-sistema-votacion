import time
from datetime import datetime

from flask import Flask, jsonify, request, g
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import SQLAlchemyError

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

    # ---------------------------
    # MÉTRICAS BÁSICAS
    # ISO/IEC 25010: eficiencia y confiabilidad
    # FURPS: performance y supportability
    # ---------------------------
    @app.before_request
    def start_timer():
        g.start_time = time.perf_counter()

    @app.after_request
    def add_performance_headers(response):
        if hasattr(g, "start_time"):
            elapsed_ms = (time.perf_counter() - g.start_time) * 1000
            response.headers["X-Response-Time-ms"] = f"{elapsed_ms:.2f}"
        response.headers["X-Content-Type-Options"] = "nosniff"
        return response

    # ---------------------------
    # MANEJO CENTRALIZADO DE ERRORES
    # ISO/IEC 25010: confiabilidad y mantenibilidad
    # ---------------------------
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "error": "Recurso no encontrado.",
            "codigo": 404
        }), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            "error": "Método HTTP no permitido para esta ruta.",
            "codigo": 405
        }), 405

    @app.errorhandler(SQLAlchemyError)
    def database_error(error):
        db.session.rollback()
        return jsonify({
            "error": "Ocurrió un error al procesar la operación en la base de datos.",
            "codigo": 500
        }), 500

    @app.errorhandler(Exception)
    def unexpected_error(error):
        # En pruebas, dejar que Flask propague los errores facilita detectarlos.
        if app.config.get("TESTING"):
            raise error

        return jsonify({
            "error": "Ocurrió un error interno inesperado.",
            "codigo": 500
        }), 500

    # ---------------------------
    # FUNCIONES DE VALIDACIÓN
    # ---------------------------
    def validar_correo(correo):
        return isinstance(correo, str) and "@" in correo and "." in correo.split("@")[-1]

    def validar_texto(texto, min_len=1, max_len=150):
        return (
            isinstance(texto, str)
            and min_len <= len(texto.strip()) <= max_len
        )

    # ---------------------------
    # ENDPOINTS
    # ---------------------------
    @app.get("/health")
    def health():
        return jsonify({
            "status": "ok",
            "service": "sistema-votacion",
            "database": "configured"
        }), 200

    @app.get("/metrics")
    def metrics():
        """
        Endpoint simple para evidenciar métricas del sistema.
        No sustituye una herramienta de observabilidad real.
        """
        return jsonify({
            "metricas_calidad": {
                "rendimiento_objetivo": "P95 <= 2 segundos",
                "disponibilidad_objetivo": ">= 99.5%",
                "votos_duplicados_permitidos": 0,
                "vulnerabilidades_criticas_objetivo": 0,
                "cobertura_pruebas_objetivo": ">= 80%"
            },
            "modelo_referencia": [
                "ISO/IEC 25010",
                "McCall",
                "FURPS",
                "CMMI",
                "ISO/IEC 15504 (SPICE)"
            ]
        }), 200

    @app.post("/register")
    def register():
        data = request.get_json(silent=True) or {}

        nombre = (data.get("nombre") or "").strip()
        correo = (data.get("correo") or "").strip().lower()
        password = data.get("password") or ""

        errores = {}

        if not validar_texto(nombre, 2, 120):
            errores["nombre"] = "Debe contener entre 2 y 120 caracteres."

        if not validar_correo(correo):
            errores["correo"] = "El correo no tiene un formato válido."

        if not isinstance(password, str) or len(password) < 6:
            errores["password"] = "La contraseña debe tener mínimo 6 caracteres."

        if errores:
            return jsonify({
                "error": "Datos de registro inválidos.",
                "detalles": errores
            }), 400

        if Usuario.query.filter_by(correo=correo).first():
            return jsonify({
                "error": "El correo ya está registrado."
            }), 409

        usuario = Usuario(
            nombre=nombre,
            correo=correo,
            password_hash=generate_password_hash(password)
        )

        db.session.add(usuario)
        db.session.commit()

        return jsonify({
            "mensaje": "Usuario registrado.",
            "id": usuario.id
        }), 201

    @app.post("/login")
    def login():
        data = request.get_json(silent=True) or {}

        correo = (data.get("correo") or "").strip().lower()
        password = data.get("password") or ""

        if not validar_correo(correo) or not isinstance(password, str):
            return jsonify({
                "error": "Credenciales inválidas."
            }), 400

        usuario = Usuario.query.filter_by(
            correo=correo,
            activo=True
        ).first()

        if not usuario or not check_password_hash(usuario.password_hash, password):
            return jsonify({
                "error": "Credenciales inválidas."
            }), 401

        login_user(usuario)

        return jsonify({
            "mensaje": "Inicio de sesión correcto.",
            "usuario": {
                "id": usuario.id,
                "nombre": usuario.nombre,
                "rol": usuario.rol
            }
        }), 200

    @app.post("/logout")
    @login_required
    def logout():
        logout_user()
        return jsonify({
            "mensaje": "Sesión cerrada."
        }), 200

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
                "candidatos": [
                    {
                        "id": c.id,
                        "nombre": c.nombre
                    }
                    for c in e.candidatos
                ],
            }
            for e in items
        ]), 200

    @app.post("/vote")
    @login_required
    def vote():
        data = request.get_json(silent=True) or {}

        eleccion_id = data.get("eleccion_id")
        candidato_id = data.get("candidato_id")

        if not isinstance(eleccion_id, int) or not isinstance(candidato_id, int):
            return jsonify({
                "error": "eleccion_id y candidato_id deben ser números enteros."
            }), 400

        eleccion = db.session.get(Eleccion, eleccion_id)
        candidato = db.session.get(Candidato, candidato_id)

        if not eleccion:
            return jsonify({
                "error": "La elección no existe."
            }), 404

        if not candidato:
            return jsonify({
                "error": "El candidato no existe."
            }), 404

        if candidato.eleccion_id != eleccion.id:
            return jsonify({
                "error": "El candidato no pertenece a la elección indicada."
            }), 400

        ahora = datetime.utcnow()

        if not eleccion.activa:
            return jsonify({
                "error": "La elección está inactiva."
            }), 400

        if ahora < eleccion.fecha_inicio or ahora > eleccion.fecha_fin:
            return jsonify({
                "error": "La elección no se encuentra dentro del periodo habilitado."
            }), 400

        existente = Voto.query.filter_by(
            usuario_id=current_user.id,
            eleccion_id=eleccion.id
        ).first()

        if existente:
            return jsonify({
                "error": "El usuario ya votó en esta elección."
            }), 409

        voto = Voto(
            usuario_id=current_user.id,
            eleccion_id=eleccion.id,
            candidato_id=candidato.id
        )

        db.session.add(voto)
        db.session.commit()

        return jsonify({
            "mensaje": "Voto registrado correctamente.",
            "voto_id": voto.id
        }), 201

    @app.get("/results/<int:eleccion_id>")
    @login_required
    def results(eleccion_id):
        eleccion = db.session.get(Eleccion, eleccion_id)

        if not eleccion:
            return jsonify({
                "error": "Elección no encontrada."
            }), 404

        resultados = []
        total_votos = 0

        for candidato in eleccion.candidatos:
            total = Voto.query.filter_by(candidato_id=candidato.id).count()
            total_votos += total

            resultados.append({
                "candidato": candidato.nombre,
                "votos": total
            })

        return jsonify({
            "eleccion": eleccion.nombre,
            "total_votos": total_votos,
            "resultados": resultados
        }), 200

    return app


if __name__ == "__main__":
    app = create_app()

    with app.app_context():
        db.create_all()

    app.run(debug=True)
