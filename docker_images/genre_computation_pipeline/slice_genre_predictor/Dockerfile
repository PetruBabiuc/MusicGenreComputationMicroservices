FROM tensorflow/tensorflow:2.9.1

ENV PYTHONUNBUFFERED=1

ADD . /

RUN pip install -r requirements.txt

ENTRYPOINT ["python3", "-u", "main.py"]