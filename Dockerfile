FROM python:3.13-slim

WORKDIR /app

COPY pyproject.toml ./
RUN pip install --no-cache-dir uv \
    && uv pip install --system -r pyproject.toml \
    && pip uninstall --yes uv

COPY order_service ./order_service
COPY alembic ./alembic
COPY alembic.ini ./
COPY bin ./bin

EXPOSE 8000

CMD ["sh", "-c", "python -m alembic upgrade head && python bin/main.py"]
