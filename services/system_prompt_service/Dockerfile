# services/system_prompt_service/Dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY services/system_prompt_service/ .

EXPOSE 5006
CMD ["python", "app.py"]
