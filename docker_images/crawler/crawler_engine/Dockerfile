FROM python:3.9-alpine

ENV PYTHONUNBUFFERED=1
ENV IMAGE_PATH=docker_images/crawler/crawler_engine

ADD $IMAGE_PATH/requirements.txt requirements.txt
ADD $IMAGE_PATH/main.py main.py

RUN pip install -r requirements.txt

ADD config/constants.py config/constants.py
ADD config/crawler_engine.py config/crawler_engine.py
ADD config/crawler_management_controller.py config/crawler_management_controller.py
ADD config/database_api.py config/database_api.py
ADD config/database_api_credentials.py config/database_api_credentials.py
ADD config/rabbit_mq.py config/rabbit_mq.py

ADD src/business/crawler/CrawlerEngine.py src/business/crawler/CrawlerEngine.py

ADD src/helpers/Base64Converter.py src/helpers/Base64Converter.py
ADD src/helpers/DatabaseApiProxy.py src/helpers/DatabaseApiProxy.py
ADD src/helpers/HighLevelSocketWrapper.py src/helpers/HighLevelSocketWrapper.py
ADD src/helpers/RabbitMqConsumer.py src/helpers/RabbitMqConsumer.py
ADD src/helpers/RabbitMqProducer.py src/helpers/RabbitMqProducer.py

ADD src/helpers/abstract_classes/AbstractRabbitMqClient.py src/helpers/abstract_classes/AbstractRabbitMqClient.py
ADD src/helpers/abstract_classes/AsyncMessageConsumerInterface.py src/helpers/abstract_classes/AsyncMessageConsumerInterface.py
ADD src/helpers/abstract_classes/MessageProducerInterface.py src/helpers/abstract_classes/MessageProducerInterface.py
ADD src/helpers/abstract_classes/SyncMessageConsumerInterface.py src/helpers/abstract_classes/SyncMessageConsumerInterface.py

ADD src/AbstractMicroservice.py src/AbstractMicroservice.py

ENTRYPOINT ["python3", "main.py"]