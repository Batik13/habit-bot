FROM python:3.11-slim
WORKDIR /app

# System deps (tzdata optional)
RUN apt-get update -y && apt-get install -y --no-install-recommends tzdata && rm -rf /var/lib/apt/lists/*

# Copy and install
COPY pyproject.toml requirements.txt* ./
RUN pip install --no-cache-dir -r requirements.txt || true
COPY . .

# Expose and run
ENV HOST=0.0.0.0 PORT=8080
EXPOSE 8080
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]