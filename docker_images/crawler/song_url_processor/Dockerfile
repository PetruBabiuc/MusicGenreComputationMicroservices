FROM python:3.9-alpine

ENV PYTHONUNBUFFERED=1
ENV IMAGE_PATH=docker_images/crawler/song_url_processor

ADD $IMAGE_PATH/main.py main.py
ADD $IMAGE_PATH/requirements.txt requirements.txt

RUN pip install -r requirements.txt

ADD config/constants.py config/constants.py
ADD config/crawler_genre_obtainer.py config/crawler_genre_obtainer.py
ADD config/rabbit_mq.py config/rabbit_mq.py

ADD src/AbstractMicroservice.py src/AbstractMicroservice.py

ADD src/business/crawler/Mp3ProcessorMicroservice.py src/business/crawler/Mp3ProcessorMicroservice.py

ADD src/helpers/Base64Converter.py src/helpers/Base64Converter.py
ADD src/helpers/HighLevelSocketWrapper.py src/helpers/HighLevelSocketWrapper.py
ADD src/helpers/RabbitMqConsumer.py src/helpers/RabbitMqConsumer.py
ADD src/helpers/RabbitMqProducer.py src/helpers/RabbitMqProducer.py

ADD src/helpers/abstract_classes/AbstractRabbitMqClient.py src/helpers/abstract_classes/AbstractRabbitMqClient.py
ADD src/helpers/abstract_classes/AsyncMessageConsumerInterface.py src/helpers/abstract_classes/AsyncMessageConsumerInterface.py
ADD src/helpers/abstract_classes/MessageProducerInterface.py src/helpers/abstract_classes/MessageProducerInterface.py
ADD src/helpers/abstract_classes/SyncMessageConsumerInterface.py src/helpers/abstract_classes/SyncMessageConsumerInterface.py

ENTRYPOINT ["python3", "main.py"]