# services/general_chat_service/Dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY services/general_chat_service/ .

EXPOSE 5002
CMD ["python", "app.py"]
