FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY main.py .

# Railway dynamic port use karta hai, isliye EXPOSE ki zaroorat nahi hoti (hata diya)

# Run the application using Flask/Python instead of Uvicorn
CMD ["python", "main.py"]