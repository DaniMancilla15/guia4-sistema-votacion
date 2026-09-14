DROP TABLE IF EXISTS votos CASCADE;
DROP TABLE IF EXISTS candidatos CASCADE;
DROP TABLE IF EXISTS elecciones CASCADE;
DROP TABLE IF EXISTS usuarios CASCADE;

CREATE TABLE usuarios (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(120) NOT NULL,
    correo VARCHAR(150) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    rol VARCHAR(20) NOT NULL DEFAULT 'votante',
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    creado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE elecciones (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(160) NOT NULL,
    descripcion TEXT,
    fecha_inicio TIMESTAMP NOT NULL,
    fecha_fin TIMESTAMP NOT NULL,
    activa BOOLEAN NOT NULL DEFAULT TRUE,
    CHECK (fecha_fin > fecha_inicio)
);

CREATE TABLE candidatos (
    id SERIAL PRIMARY KEY,
    eleccion_id INTEGER NOT NULL REFERENCES elecciones(id) ON DELETE CASCADE,
    nombre VARCHAR(120) NOT NULL,
    propuesta TEXT
);

CREATE TABLE votos (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    eleccion_id INTEGER NOT NULL REFERENCES elecciones(id) ON DELETE CASCADE,
    candidato_id INTEGER NOT NULL REFERENCES candidatos(id) ON DELETE CASCADE,
    creado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_usuario_eleccion UNIQUE (usuario_id, eleccion_id)
);

CREATE INDEX idx_votos_eleccion ON votos(eleccion_id);
CREATE INDEX idx_votos_candidato ON votos(candidato_id);
CREATE INDEX idx_candidatos_eleccion ON candidatos(eleccion_id);
