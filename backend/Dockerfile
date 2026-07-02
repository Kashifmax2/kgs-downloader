FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# --- SABSE ZAROORI PART ---
# Yeh command har build ke waqt yt-dlp ko latest version par update karegi
RUN pip install -U yt-dlp
# --------------------------

# Copy application code
# AGAR tumhari main.py 'backend' folder ke andar hai, toh COPY backend/main.py . karna
COPY main.py .

# Run the application
CMD ["python", "main.py"]