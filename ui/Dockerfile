# ui/Dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ui/ .

EXPOSE 7860
CMD ["python", "gradio_app.py"]
