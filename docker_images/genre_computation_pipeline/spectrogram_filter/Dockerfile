FROM python:3.9-alpine

ENV PYTHONUNBUFFERED=1
ENV IMAGE_PATH=docker_images/genre_computation_pipeline/spectrogram_filter

ADD $IMAGE_PATH/main.py main.py
ADD $IMAGE_PATH/requirements.txt requirements.txt

RUN pip install -r requirements.txt

ADD src/AbstractMicroservice.py src/AbstractMicroservice.py

ADD config/constants.py config/constants.py
ADD config/genre_computer_request_manager.py config/genre_computer_request_manager.py
ADD config/slice_genre_aggregator.py config/slice_genre_aggregator.py
ADD config/spectrogram_filter.py config/spectrogram_filter.py
ADD config/spectrogram_queue.py config/spectrogram_queue.py

ADD src/business/abstract_classes/AbstractPipelineStage.py src/business/abstract_classes/AbstractPipelineStage.py
ADD src/business/abstract_classes/AbstractSyncReceivePipelineStage.py src/business/abstract_classes/AbstractSyncReceivePipelineStage.py

ADD src/business/genre_predictor_pipeline/SpectrogramFilter.py src/business/genre_predictor_pipeline/SpectrogramFilter.py

ADD src/helpers/HighLevelSocketWrapper.py src/helpers/HighLevelSocketWrapper.py

ADD src/helpers/abstract_classes/MessageProducerInterface.py src/helpers/abstract_classes/MessageProducerInterface.py
ADD src/helpers/abstract_classes/SyncMessageConsumerInterface.py src/helpers/abstract_classes/SyncMessageConsumerInterface.py



ENTRYPOINT ["python3", "main.py"]