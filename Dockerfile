FROM python:3.9-slim
ENV PYTHONUNBUFFERED 1

WORKDIR /app
COPY requirements.txt .
RUN pip install --upgrade pip setuptools

RUN pip install -r requirements.txt

COPY . .

CMD ["python", "app.py"]