# Simple Solution Testcase

## Overview
Deribit price fetcher and FastAPI service with PostgreSQL backend.

## Design Decisions
- FastAPI for async API and auto documentation
- Celery for periodic tasks
- PostgreSQL for persistent storage
- aiohttp for async HTTP client
- Docker for containerized deployment