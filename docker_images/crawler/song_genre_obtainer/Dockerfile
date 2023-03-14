FROM python:3.9-alpine

ENV PYTHONUNBUFFERED=1
ENV IMAGE_PATH=docker_images/crawler/song_genre_obtainer

ADD $IMAGE_PATH/main.py main.py
ADD $IMAGE_PATH/requirements.txt requirements.txt

RUN pip install -r requirements.txt

ADD src/AbstractMicroservice.py src/AbstractMicroservice.py

ADD config/constants.py config/constants.py
ADD config/crawler_genre_obtainer.py config/crawler_genre_obtainer.py
ADD config/database_api.py config/database_api.py
ADD config/database_api_credentials.py config/database_api_credentials.py
ADD config/dnn.py config/dnn.py
ADD config/genre_computer_request_manager.py config/genre_computer_request_manager.py

ADD src/business/crawler/SongGenreObtainer.py src/business/crawler/SongGenreObtainer.py

ADD src/helpers/DatabaseApiProxy.py src/helpers/DatabaseApiProxy.py
ADD src/helpers/HighLevelSocketWrapper.py src/helpers/HighLevelSocketWrapper.py
ADD src/helpers/SocketJsonMessageAwaiter.py src/helpers/SocketJsonMessageAwaiter.py
ADD src/helpers/SynchronizedDict.py src/helpers/SynchronizedDict.py

ADD src/helpers/abstract_classes/AbstractMessageAwaiter.py src/helpers/abstract_classes/AbstractMessageAwaiter.py
ADD src/helpers/abstract_classes/MessageProducerInterface.py src/helpers/abstract_classes/MessageProducerInterface.py
ADD src/helpers/abstract_classes/SyncMessageConsumerInterface.py src/helpers/abstract_classes/SyncMessageConsumerInterface.py

ADD src/model/AwaitableResult.py src/model/AwaitableResult.py

ENTRYPOINT ["python3", "main.py"]