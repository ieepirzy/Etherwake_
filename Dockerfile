FROM python:3.12-slim
COPY main.py /app/wake_server.py
CMD ["python","-u", "/app/wake_server.py"]