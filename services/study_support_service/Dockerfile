# services/study_support_service/Dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY services/study_support_service/ .

EXPOSE 5003
CMD ["python", "app.py"]
