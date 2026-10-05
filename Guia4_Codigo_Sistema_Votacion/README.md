

## Mejoras para Guía 5

Se agregaron validaciones, manejo centralizado de errores, medición de tiempo de respuesta y el endpoint:

```text
GET /metrics
```

También se ampliaron las pruebas automáticas.

Ejecutar:

```bash
pytest -v
```

Para verificar el tiempo de respuesta, revisa en Postman el header:

```text
X-Response-Time-ms
```
