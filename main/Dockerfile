# main/Dockerfile

FROM python:3.9-slim

WORKDIR /app

COPY main/ /app/main/
COPY db/ /app/db/
COPY requirements_main.txt /app/

RUN pip install --no-cache-dir -r requirements_main.txt

EXPOSE 5000

CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
