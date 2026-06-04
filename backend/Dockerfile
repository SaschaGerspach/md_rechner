# Python pinned to the project's interpreter (venv runs 3.13) for dev-prod parity.
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# entrypoint runs migrate, then execs the command below (or the dev override).
ENTRYPOINT ["sh", "/app/entrypoint.sh"]

# Production default: gunicorn serving the project's WSGI app.
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
