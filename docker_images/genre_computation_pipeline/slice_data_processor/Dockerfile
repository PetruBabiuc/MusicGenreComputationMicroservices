FROM python:3.9-slim

ENV PYTHONUNBUFFERED=1
ENV IMAGE_PATH=docker_images/genre_computation_pipeline/slice_data_processor

ADD $IMAGE_PATH/main.py main.py
ADD $IMAGE_PATH/requirements.txt requirements.txt

RUN pip install -r requirements.txt

ADD src/AbstractMicroservice.py src/AbstractMicroservice.py

ADD config/dnn.py config/dnn.py
ADD config/genre_computer_request_manager.py config/genre_computer_request_manager.py
ADD config/rabbit_mq.py config/rabbit_mq.py
ADD config/slice_genre_aggregator.py config/slice_genre_aggregator.py

ADD src/business/abstract_classes/AbstractAsyncReceivePipelineStage.py src/business/abstract_classes/AbstractAsyncReceivePipelineStage.py
ADD src/business/abstract_classes/AbstractPipelineStage.py src/business/abstract_classes/AbstractPipelineStage.py

ADD src/business/genre_predictor_pipeline/SliceDataProcessor.py src/business/genre_predictor_pipeline/SliceDataProcessor.py

ADD src/helpers/HighLevelSocketWrapper.py src/helpers/HighLevelSocketWrapper.py
ADD src/helpers/RabbitMqConsumer.py src/helpers/RabbitMqConsumer.py

ADD src/helpers/abstract_classes/AbstractRabbitMqClient.py src/helpers/abstract_classes/AbstractRabbitMqClient.py
ADD src/helpers/abstract_classes/AsyncMessageConsumerInterface.py src/helpers/abstract_classes/AsyncMessageConsumerInterface.py
ADD src/helpers/abstract_classes/MessageProducerInterface.py src/helpers/abstract_classes/MessageProducerInterface.py
ADD src/helpers/abstract_classes/SyncMessageConsumerInterface.py src/helpers/abstract_classes/SyncMessageConsumerInterface.py


ENTRYPOINT ["python3", "main.py"]