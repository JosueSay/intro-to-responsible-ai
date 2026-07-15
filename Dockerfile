# Imagen del Provider (server.py). App pura stdlib, sin dependencias.
FROM python:3.12-slim

WORKDIR /app

# Solo lo que el servidor necesita en runtime.
COPY moderation.py server.py client.py config.yml ./

# Puerto interno del contenedor (coincide con port de config.yml).
EXPOSE 8000

CMD ["python", "-u", "server.py"]
