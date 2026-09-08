# PruebasPsico — Sistema de Votaciones

API RESTful desarrollada con Python, FastAPI, SQLAlchemy y PostgreSQL. Impide votos duplicados mediante validación transaccional y una restricción `UNIQUE` en la base de datos. Incluye JWT, paginación, Swagger y pruebas automáticas.

![Estadísticas](docs/statistics-api.png)

## Inicio rápido con Docker (recomendado)

Requisitos: Docker Desktop con Docker Compose.

**Windows:** ejecutar `start.bat` o `./start.ps1` desde PowerShell.

**Linux/macOS:** `chmod +x start.sh && ./start.sh`

La API estará en http://localhost:8000 y Swagger en http://localhost:8000/docs. La primera ejecución crea automáticamente la base de datos y sus tablas.

Credenciales de demostración: `admin` / `admin123`. Antes de una entrega real, cambia `ADMIN_PASSWORD` y `JWT_SECRET` en `.env`.

## Ejecución local sin Docker

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
```

Sin `DATABASE_URL` se usa SQLite para facilitar el desarrollo. Para PostgreSQL configura, por ejemplo: `postgresql+psycopg://usuario:clave@localhost/voting`.

## Ejemplos con curl

Obtener el JWT:

```bash
curl -X POST http://localhost:8000/auth/token -H "Content-Type: application/x-www-form-urlencoded" -d "username=admin&password=admin123"
```

Guarda el valor `access_token` como `TOKEN`. Crear candidato y votante:

```bash
curl -X POST http://localhost:8000/candidates -H "Authorization: Bearer TOKEN" -H "Content-Type: application/json" -d '{"name":"Ana Pérez","party":"Partido A"}'
curl -X POST http://localhost:8000/voters -H "Authorization: Bearer TOKEN" -H "Content-Type: application/json" -d '{"name":"Luis Gómez","email":"luis@example.com"}'
```

Emitir voto y consultar estadísticas:

```bash
curl -X POST http://localhost:8000/votes -H "Content-Type: application/json" -d '{"voter_id":1,"candidate_id":1}'
curl http://localhost:8000/votes/statistics
```

Todos los endpoints solicitados están disponibles en Swagger. Las listas aceptan `skip` y `limit` (máximo 100). La creación/eliminación y las listas sensibles requieren JWT; candidatos, emisión de voto y estadísticas son públicos.

## Pruebas

```bash
pytest -q
```

Las pruebas cubren el flujo completo, voto único, candidato inválido, exclusión votante/candidato y protección JWT.

## Reglas de integridad

- El correo del votante es único.
- El nombre normalizado no puede aparecer simultáneamente como votante y candidato.
- Un votante solo puede votar una vez (`UNIQUE(voter_id)`).
- La emisión bloquea las filas involucradas, crea el voto, marca `has_voted` e incrementa `candidate.votes` en una única transacción.
- No se eliminan votantes que ya votaron ni candidatos que recibieron votos.
- Las estadísticas usan funciones `lambda` y `map` para la transformación funcional solicitada.

## Estructura

```text
app/              API, modelos, esquemas, autenticación y configuración
tests/            pruebas automatizadas
docs/             captura de ejemplo de estadísticas
Dockerfile        imagen de la API
docker-compose.yml PostgreSQL + API
start.*           scripts de inicio multiplataforma
```

