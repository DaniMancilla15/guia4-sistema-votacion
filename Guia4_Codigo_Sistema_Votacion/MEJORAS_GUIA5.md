# Mejoras aplicadas para la Guía 5

## Objetivo
Aplicar modelos, estándares y métricas de calidad al Sistema Web de Votación sin cambiar su arquitectura principal.

## Cambios realizados

1. **Validación de datos de entrada**
   - Nombre entre 2 y 120 caracteres.
   - Validación básica del formato de correo.
   - Contraseña mínima de 6 caracteres.
   - IDs de elección y candidato deben ser enteros.

2. **Manejo centralizado de errores**
   - Respuestas JSON para 404 y 405.
   - Manejo de errores de base de datos.
   - Rollback automático ante errores SQLAlchemy.

3. **Métrica de tiempo de respuesta**
   - Cada respuesta incluye el header `X-Response-Time-ms`.
   - Sirve como evidencia de una métrica de eficiencia/rendimiento.

4. **Nuevo endpoint `/metrics`**
   - Expone objetivos de calidad del proyecto:
     - P95 <= 2 segundos.
     - Disponibilidad >= 99.5 %.
     - 0 votos duplicados.
     - 0 vulnerabilidades críticas.
     - Cobertura de pruebas >= 80 %.

5. **Mayor cobertura de pruebas**
   - Health check.
   - Métricas.
   - Registro inválido.
   - Registro/login.
   - Listado de elecciones.
   - Voto único.
   - Candidato asociado a elección incorrecta.
   - Resultados.
   - Error 404 en JSON.

## Relación con modelos y estándares

- **ISO/IEC 25010**
  - Confiabilidad: manejo de errores.
  - Seguridad: validación y hash de contraseñas.
  - Eficiencia: medición de tiempo de respuesta.
  - Mantenibilidad: separación de validaciones y manejo centralizado de errores.

- **McCall**
  - Integridad: evita voto duplicado.
  - Testabilidad: pruebas automáticas ampliadas.
  - Eficiencia: métrica de tiempo de respuesta.

- **FURPS**
  - Functionality: validaciones de funcionalidades principales.
  - Reliability: respuestas controladas ante errores.
  - Performance: header de tiempo de respuesta.
  - Supportability: código y respuestas más fáciles de diagnosticar.

- **CMMI / SPICE**
  - Se fortalece el proceso mediante evidencias, pruebas, criterios de calidad y documentación.
