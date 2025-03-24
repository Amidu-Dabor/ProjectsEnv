# services/auth_service/Dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY services/auth_service/ .

EXPOSE 5001
CMD ["python", "app.py"]
