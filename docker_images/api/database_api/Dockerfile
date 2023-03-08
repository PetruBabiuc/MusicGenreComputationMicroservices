FROM python:3.9

ENV PYTHONUNBUFFERED=1

ADD . /

RUN apt-get update &&  \
    apt-get install libmariadb3 libmariadb-dev

RUN pip install -r requirements.txt

ENTRYPOINT ["python3", "main.py"]