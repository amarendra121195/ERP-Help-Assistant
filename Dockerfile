FROM python:3.12-slim-bookworm

# Microsoft ODBC Driver 18, needed by pyodbc to reach SQL Server from Linux
RUN apt-get update && apt-get install -y --no-install-recommends curl gnupg unixodbc \
    && curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /usr/share/keyrings/microsoft-prod.gpg \
    && curl -fsSL https://packages.microsoft.com/config/debian/12/prod.list -o /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update && ACCEPT_EULA=Y apt-get install -y --no-install-recommends msodbcsql18 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY data ./data

EXPOSE 8000
# Build the vector index on first start (needs OPENAI_API_KEY), then serve the API.
CMD ["sh", "-c", "[ -d vectorstore ] || python -m app.rag.ingest; uvicorn app.main:app --host 0.0.0.0 --port 8000"]
