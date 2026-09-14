import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "cambiar-esta-clave")
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://postgres:postgres@localhost:5432/votacion_db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
