#!/bin/bash
set -e
echo "Aplicando migrações do banco de dados..."
alembic upgrade head
echo "Iniciando o servidor FastAPI..."
exec uvicorn main:app --host 0.0.0.0 --port 8000