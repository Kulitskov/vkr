# analytics/Dockerfile

FROM python:3.9-slim

WORKDIR /app

COPY analytics/ /app/analytics/
COPY db/ /app/db/
COPY requirements_analytics.txt /app/

RUN pip install --no-cache-dir -r requirements_analytics.txt

EXPOSE 5002

CMD ["python", "analytics/service_analytics.py"]
