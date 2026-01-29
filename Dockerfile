FROM python:3.10-slim

WORKDIR /app
COPY . /app

ENV PYTHONPATH=/app/src

RUN pip install -r requirements.txt

CMD ["python"]
