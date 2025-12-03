FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for opencv, insightface and build tools
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libgomp1 \
    build-essential \
    g++ \
    cmake \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Upgrade pip
RUN pip install --upgrade pip

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir fastapi uvicorn[standard] sqlalchemy psycopg2-binary python-multipart cloudinary python-jose[cryptography] passlib[bcrypt] pydantic[email] email-validator

# Copy application code
COPY . .

# Expose the port
EXPOSE 8081

# Run the FastAPI application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8081", "--reload"]
