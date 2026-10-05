INSERT INTO elecciones (nombre, descripcion, fecha_inicio, fecha_fin, activa)
VALUES (
    'Elección representante 2026',
    'Elección académica de demostración para la Guía 3.',
    CURRENT_TIMESTAMP - INTERVAL '1 day',
    CURRENT_TIMESTAMP + INTERVAL '30 day',
    TRUE
);

INSERT INTO candidatos (eleccion_id, nombre, propuesta)
VALUES
(1, 'Ana Torres', 'Mejorar canales de comunicación.'),
(1, 'Carlos Ruiz', 'Fortalecer actividades estudiantiles.'),
(1, 'Laura Díaz', 'Impulsar iniciativas de bienestar.');
