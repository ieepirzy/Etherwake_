FROM python:3.12-slim
COPY wake_server.py /app/wake_server.py
CMD ["python", "/app/wake_server.py"]