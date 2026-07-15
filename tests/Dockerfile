# Imagen del set de pruebas: pytest + la logica a probar.
FROM python:3.12-slim

WORKDIR /app
ENV PYTHONPATH=/app

# pytest (unica dependencia de dev; la app es stdlib).
COPY requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements-dev.txt

# Codigo bajo prueba + suite.
COPY moderation.py client.py config.yml pytest.ini ./
COPY tests ./tests

CMD ["pytest"]
