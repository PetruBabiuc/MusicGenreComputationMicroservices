FROM python:3.9-alpine

ENV PYTHONUNBUFFERED=1
ENV IMAGE_PATH=docker_images/song_validator

ADD $IMAGE_PATH/main.py main.py
ADD $IMAGE_PATH/requirements.txt requirements.txt

RUN pip install -r requirements.txt

ADD src/AbstractMicroservice.py src/AbstractMicroservice.py

ADD config/constants.py config/constants.py
ADD config/mp3_validator.py config/mp3_validator.py
ADD config/rabbit_mq.py config/rabbit_mq.py
ADD config/redis.py config/redis.py

ADD src/business/Mp3Validator.py src/business/Mp3Validator.py

ADD src/helpers/Base64Converter.py src/helpers/Base64Converter.py
ADD src/helpers/RabbitMqConsumer.py src/helpers/RabbitMqConsumer.py

ADD src/helpers/abstract_classes/AbstractRabbitMqClient.py src/helpers/abstract_classes/AbstractRabbitMqClient.py
ADD src/helpers/abstract_classes/AsyncMessageConsumerInterface.py src/helpers/abstract_classes/AsyncMessageConsumerInterface.py

ENTRYPOINT ["python3", "main.py"]