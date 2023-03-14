FROM python:3.9-alpine

ENV PYTHONUNBUFFERED=1
ENV IMAGE_PATH=docker_images/

ADD $IMAGE_PATH/main.py main.py
ADD $IMAGE_PATH/requirements.txt requirements.txt

RUN pip install -r requirements.txt

ADD src/AbstractMicroservice.py src/AbstractMicroservice.py

ENTRYPOINT ["python3", "main.py"]