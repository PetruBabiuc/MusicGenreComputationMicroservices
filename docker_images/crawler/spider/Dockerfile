FROM python:3.9-slim

ENV PYTHONUNBUFFERED=1

RUN apt-get update && \
    apt-get install -y python3-dev \
    gcc \
    libc-dev

ADD . /

RUN pip install -r requirements.txt

ENTRYPOINT ["python3", "main.py"]