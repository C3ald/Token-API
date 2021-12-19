# Dockerfile, Image, Container
FROM python:3.9.5

WORKDIR /Token-app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY main.py .

CMD ["python", "./main.py"]