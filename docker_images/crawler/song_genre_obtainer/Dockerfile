FROM python:3.9-alpine

ENV PYTHONUNBUFFERED=1

ADD . /

RUN pip install -r requirements.txt

ENTRYPOINT ["python3", "main.py"]