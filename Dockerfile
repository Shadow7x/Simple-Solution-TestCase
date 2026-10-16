FROM python:3.14-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/


COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --dev --no-install-project

COPY . .

CMD ["uv", "run", "uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
