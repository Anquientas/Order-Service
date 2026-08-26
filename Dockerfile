FROM python:3.13-slim

WORKDIR /app

COPY pyproject.toml README.md ./
COPY order_service ./order_service
RUN pip install --no-cache-dir uv \
    && uv pip install --system . \
    && pip uninstall --yes uv

COPY alembic ./alembic
COPY alembic.ini ./
COPY bin ./bin
RUN chmod +x bin/start.sh

EXPOSE 8000

CMD ["bash", "bin/start.sh"]
