# Sistema Web de Votación - Guía 3

Proyecto de referencia para aplicar ISO/IEC 29110 y un plan de pruebas.

## Requisitos
- Python 3.11+
- PostgreSQL
- pip

## 1. Crear base de datos
En PostgreSQL:

```sql
CREATE DATABASE votacion_db;
```

Luego ejecutar:

```bash
psql -U postgres -d votacion_db -f schema.sql
psql -U postgres -d votacion_db -f seed.sql
```

## 2. Crear entorno e instalar dependencias

```bash
python -m venv venv
```

Windows:
```bash
venv\Scripts\activate
```

Linux/macOS:
```bash
source venv/bin/activate
```

Instalar:
```bash
pip install -r requirements.txt
```

## 3. Configurar conexión

Linux/macOS:
```bash
export DATABASE_URL="postgresql+psycopg2://postgres:TU_CLAVE@localhost:5432/votacion_db"
export SECRET_KEY="una-clave-segura"
```

Windows PowerShell:
```powershell
$env:DATABASE_URL="postgresql+psycopg2://postgres:TU_CLAVE@localhost:5432/votacion_db"
$env:SECRET_KEY="una-clave-segura"
```

## 4. Ejecutar

```bash
python app.py
```

La API queda en:
`http://127.0.0.1:5000`

## 5. Ejecutar pruebas

```bash
pytest -v
```

## Endpoints principales
- `GET /health`
- `POST /register`
- `POST /login`
- `POST /logout`
- `GET /elecciones`
- `POST /vote`
- `GET /results/<eleccion_id>`

## Ejemplo registro
```json
{
  "nombre": "Daniela",
  "correo": "daniela@example.com",
  "password": "123456"
}
```

## Ejemplo voto
```json
{
  "eleccion_id": 1,
  "candidato_id": 1
}
```
