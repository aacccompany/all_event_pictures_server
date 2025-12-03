FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for opencv and insightface
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir fastapi uvicorn[standard] sqlalchemy psycopg2-binary python-multipart cloudinary python-jose[cryptography] passlib[bcrypt]

# Copy application code
COPY . .

# Expose the port
EXPOSE 8081

# Run the FastAPI application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8081", "--reload"]
