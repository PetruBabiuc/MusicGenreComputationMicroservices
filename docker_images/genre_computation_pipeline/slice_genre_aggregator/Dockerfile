FROM python:3.9-alpine

ENV PYTHONUNBUFFERED=1
ENV IMAGE_PATH=docker_images/genre_computation_pipeline/slice_genre_aggregator

ADD $IMAGE_PATH/main.py main.py
ADD $IMAGE_PATH/requirements.txt requirements.txt

RUN pip install -r requirements.txt

ADD src/AbstractMicroservice.py src/AbstractMicroservice.py

ADD config/genre_computer_request_manager.py config/genre_computer_request_manager.py
ADD config/slice_genre_aggregator.py config/slice_genre_aggregator.py

ADD src/business/genre_predictor_pipeline/SliceGenreAggregator.py src/business/genre_predictor_pipeline/SliceGenreAggregator.py

ADD src/helpers/Base64Converter.py src/helpers/Base64Converter.py
ADD src/helpers/HighLevelSocketWrapper.py src/helpers/HighLevelSocketWrapper.py
ADD src/helpers/SynchronizedDict.py src/helpers/SynchronizedDict.py

ADD src/helpers/abstract_classes/MessageProducerInterface.py src/helpers/abstract_classes/MessageProducerInterface.py
ADD src/helpers/abstract_classes/SyncMessageConsumerInterface.py src/helpers/abstract_classes/SyncMessageConsumerInterface.py

ADD src/model/SongGenresPack.py src/model/SongGenresPack.py

ENTRYPOINT ["python3", "main.py"]