FROM python:3.11-slim

WORKDIR /app

RUN groupadd -r ctem && useradd -r -g ctem ctem

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY alembic.ini .
COPY alembic/ alembic/
COPY run.py .
COPY app/ app/

RUN chown -R ctem:ctem /app
USER ctem

EXPOSE 8000

CMD alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000
