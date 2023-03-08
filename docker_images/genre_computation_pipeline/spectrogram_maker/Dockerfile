FROM python:3.9

ENV PYTHONUNBUFFERED=1

RUN apt-get update -y && apt-get install -y \
  libmagic-dev \
  sox \
  libsox-fmt-mp3 \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

ADD . /

RUN pip install -r requirements.txt

ENTRYPOINT ["python3", "main.py"]