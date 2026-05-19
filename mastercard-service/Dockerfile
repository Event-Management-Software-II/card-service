FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN prisma generate

EXPOSE 3003

CMD ["python", "run.py"]
