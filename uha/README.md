# uha

A modern FastAPI project with clean architecture

Created on 2025-09-05 by eun2ce

## Installation

```bash
uv sync --dev
```

## Development

```bash
cd projects/uha-backend
uvicorn uha.backend.main:app --reload
```

## Project Structure

```
├── features/                           # Shared kernel modules
│   ├── uha-shared_kernel/
│   ├── uha-shared_kernel-infra-fastapi/
│   └── uha-shared-kernel-infra-database-sqla/
└── projects/                           # Main applications
    └── uha-backend/
```
