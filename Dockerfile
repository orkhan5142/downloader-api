FROM python:3.11-slim

WORKDIR /app

# Lazım olan sistem paketlərini quraşdır
RUN apt-get update && apt-get install -y \
    git gcc g++ make ffmpeg poppler-utils libmupdf-dev libleptonica-dev libtesseract-dev swig \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Torch olmadan requirements yüklə
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Proyektin fayllarını kopyala
COPY . .

# Torch-u runtime-da yüklə və app-i işə sal
CMD ["sh", "-c", "pip install torch==2.7.0 && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
