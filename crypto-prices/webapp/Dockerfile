# Start with a Python base image
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY webapp.py .

EXPOSE 8080

CMD ["python", "webapp.py"]
