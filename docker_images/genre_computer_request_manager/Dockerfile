FROM python:3.9-alpine

ENV PYTHONUNBUFFERED=1
ENV IMAGE_PATH=docker_images/genre_computer_request_manager

ADD $IMAGE_PATH/main.py main.py
ADD $IMAGE_PATH/requirements.txt requirements.txt

RUN pip install -r requirements.txt

ADD src/AbstractMicroservice.py src/AbstractMicroservice.py

ADD config/crawler_genre_obtainer.py config/crawler_genre_obtainer.py
ADD config/database_api.py config/database_api.py
ADD config/database_api_credentials.py config/database_api_credentials.py
ADD config/genre_computer_request_manager.py config/genre_computer_request_manager.py
ADD config/rabbit_mq.py config/rabbit_mq.py
ADD config/song_adder_controller.py config/song_adder_controller.py

ADD src/business/GenreComputerRequestManager.py src/business/GenreComputerRequestManager.py

ADD src/helpers/Base64Converter.py src/helpers/Base64Converter.py
ADD src/helpers/DatabaseApiProxy.py src/helpers/DatabaseApiProxy.py
ADD src/helpers/HighLevelSocketWrapper.py src/helpers/HighLevelSocketWrapper.py
ADD src/helpers/RabbitMqProducer.py src/helpers/RabbitMqProducer.py
ADD src/helpers/SynchronizedDict.py src/helpers/SynchronizedDict.py

ADD src/helpers/abstract_classes/AbstractRabbitMqClient.py src/helpers/abstract_classes/AbstractRabbitMqClient.py
ADD src/helpers/abstract_classes/MessageProducerInterface.py src/helpers/abstract_classes/MessageProducerInterface.py
ADD src/helpers/abstract_classes/SyncMessageConsumerInterface.py src/helpers/abstract_classes/SyncMessageConsumerInterface.py

ENTRYPOINT ["python3", "main.py"]