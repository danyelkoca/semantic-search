# weaviate-init/Dockerfile

FROM python:3.10-slim

WORKDIR /app

# Upgrade pip
RUN pip install --upgrade pip

COPY . .
RUN pip install -r requirements.txt

CMD ["sh", "-c", "python download_data.py && python populate_db.py"]
