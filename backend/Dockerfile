FROM python:3.11-slim

WORKDIR /app

# Versiones y hashes fijados, solo wheels (DECISIÓN 082; SonarCloud S8541 y S8544).
COPY requirements.lock .
RUN pip install --no-cache-dir --only-binary :all: --require-hashes -r requirements.lock

# Solo lo que la imagen usa, no el contexto entero (SonarCloud S6470). tests/ entra porque el smoke del
# despliegue corre pytest dentro de esta imagen (scripts/test.sh smoke).
COPY alembic.ini pytest.ini ./
COPY alembic ./alembic
COPY metis ./metis
COPY tests ./tests

# Usuario sin privilegios (SonarCloud S6471). El compose de desarrollo vuelve a root por el bind mount de ./backend.
RUN useradd --create-home --uid 10001 metis
USER metis

EXPOSE 8000

CMD ["uvicorn", "metis.main:app", "--host", "0.0.0.0", "--port", "8000"]
