FROM tensorflow/tensorflow:2.9.1

ENV PYTHONUNBUFFERED=1
ENV IMAGE_PATH=docker_images/genre_computation_pipeline/slice_genre_predictor

ADD $IMAGE_PATH/main.py main.py
ADD $IMAGE_PATH/requirements.txt requirements.txt

RUN pip install -r requirements.txt

ADD src/AbstractMicroservice.py src/AbstractMicroservice.py

ADD config/constants.py config/constants.py
ADD config/dnn.py config/dnn.py
ADD config/genre_computer_request_manager.py config/genre_computer_request_manager.py
ADD config/rabbit_mq.py config/rabbit_mq.py

ADD dnn dnn

ADD src/business/abstract_classes/AbstractAsyncReceivePipelineStage.py src/business/abstract_classes/AbstractAsyncReceivePipelineStage.py
ADD src/business/abstract_classes/AbstractPipelineStage.py src/business/abstract_classes/AbstractPipelineStage.py

ADD src/business/genre_predictor_pipeline/SliceGenrePredictor.py src/business/genre_predictor_pipeline/SliceGenrePredictor.py

ADD src/helpers/DnnFactory.py src/helpers/DnnFactory.py
ADD src/helpers/ImageTransformer.py src/helpers/ImageTransformer.py
ADD src/helpers/RabbitMqConsumer.py src/helpers/RabbitMqConsumer.py
ADD src/helpers/RabbitMqProducer.py src/helpers/RabbitMqProducer.py

ADD src/helpers/abstract_classes/AbstractRabbitMqClient.py src/helpers/abstract_classes/AbstractRabbitMqClient.py
ADD src/helpers/abstract_classes/AsyncMessageConsumerInterface.py src/helpers/abstract_classes/AsyncMessageConsumerInterface.py
ADD src/helpers/abstract_classes/MessageProducerInterface.py src/helpers/abstract_classes/MessageProducerInterface.py

ENTRYPOINT ["python3", "-u", "main.py"]