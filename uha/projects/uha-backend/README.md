# uha-backend

A modern FastAPI project with clean architecture

## Development

1. Install dependencies:
```bash
uv sync --dev
```

2. Set up environment variables:
```bash
cp env.example .env
# Edit .env file with your configuration
```

3. Run database migrations:
```bash
alembic upgrade head
```

4. Start the development server:
```bash
uvicorn uha.backend.main:app --reload
```

## API Documentation

Once the server is running, you can access:
- OpenAPI docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
