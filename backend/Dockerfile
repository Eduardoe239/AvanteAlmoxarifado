FROM python:3.11-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
RUN apt-get update && apt-get install -y libpq-dev gcc tesseract-ocr tesseract-ocr-por && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN chmod +x start.sh
EXPOSE 8000

# start.sh roda "alembic upgrade head" antes de subir o servidor, então o
# schema do banco fica sempre sincronizado com as migrações versionadas
# em alembic/versions/ antes da aplicação aceitar requisições.
CMD ["./start.sh"]
