FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p database uploads logs backups certificates flask_session

EXPOSE 8080

CMD ["python", "server.py"]
