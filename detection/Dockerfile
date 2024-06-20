# detection/Dockerfile

FROM python:3.9-slim

WORKDIR /app

COPY detection/ /app/detection/
COPY db/ /app/db/
COPY requirements_detection.txt /app/

RUN pip install --no-cache-dir -r requirements_detection.txt

EXPOSE 5001

CMD ["python", "detection/process.py"]
