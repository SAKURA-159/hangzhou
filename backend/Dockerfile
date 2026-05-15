FROM python:3.11-slim

WORKDIR /app

# Install backend dependencies
COPY pyproject.toml .
RUN pip install --no-cache-dir -e ".[dev]" && pip uninstall -y bcrypt passlib 2>/dev/null; pip install --no-cache-dir bcrypt

COPY . .

# Create data directory for SQLite
RUN mkdir -p /app/data

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
