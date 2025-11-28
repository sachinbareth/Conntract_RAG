# Base Python image
FROM python:3.11-slim

# Avoid prompt issues
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies needed for PyPDF2, FAISS, psycopg2
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Copy only dependency file first (layer caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy full project
COPY . .

# Expose FastAPI port
EXPOSE 8000

# Run FastAPI using uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
