# services/response_service/Dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY services/response_service/ .

EXPOSE 5005
CMD ["python", "app.py"]
