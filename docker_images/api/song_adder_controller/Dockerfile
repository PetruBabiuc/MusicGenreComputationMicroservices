FROM python:3.9-alpine

ENV PYTHONUNBUFFERED=1
ENV IMAGE_PATH=docker_images/api/song_adder_controller

ADD $IMAGE_PATH/requirements.txt requirements.txt
RUN pip install -r requirements.txt
ADD $IMAGE_PATH/main.py main.py

ADD config/constants.py config/constants.py
ADD config/database_api.py config/database_api.py
ADD config/database_api_credentials.py config/database_api_credentials.py
ADD config/front_end.py config/front_end.py
ADD config/genre_computer_request_manager.py config/genre_computer_request_manager.py
ADD config/jwt.py config/jwt.py
ADD config/rabbit_mq.py config/rabbit_mq.py
ADD config/redis.py config/redis.py
ADD config/song_adder_controller.py config/song_adder_controller.py
ADD config/user_types.py config/user_types.py

ADD src/AbstractMicroservice.py src/AbstractMicroservice.py

ADD src/helpers/abstract_classes/AbstractMessageAwaiter.py src/helpers/abstract_classes/AbstractMessageAwaiter.py
ADD src/helpers/abstract_classes/AbstractRabbitMqClient.py src/helpers/abstract_classes/AbstractRabbitMqClient.py
ADD src/helpers/abstract_classes/MessageProducerInterface.py src/helpers/abstract_classes/MessageProducerInterface.py
ADD src/helpers/abstract_classes/Mp3ValidatorProxyInterface.py src/helpers/abstract_classes/Mp3ValidatorProxyInterface.py
ADD src/helpers/abstract_classes/SyncMessageConsumerInterface.py src/helpers/abstract_classes/SyncMessageConsumerInterface.py

ADD src/helpers/security/FastApiJwtManager.py src/helpers/security/FastApiJwtManager.py
ADD src/helpers/security/JwtManager.py src/helpers/security/JwtManager.py
ADD src/helpers/security/PasswordManager.py src/helpers/security/PasswordManager.py

ADD src/helpers/Base64Converter.py src/helpers/Base64Converter.py
ADD src/helpers/DatabaseApiProxy.py src/helpers/DatabaseApiProxy.py
ADD src/helpers/HighLevelSocketWrapper.py src/helpers/HighLevelSocketWrapper.py
ADD src/helpers/Mp3ValidatorProxy.py src/helpers/Mp3ValidatorProxy.py
ADD src/helpers/RabbitMqProducer.py src/helpers/RabbitMqProducer.py
ADD src/helpers/RedisJsonMessageAwaiter.py src/helpers/RedisJsonMessageAwaiter.py
ADD src/helpers/SocketJsonMessageAwaiter.py src/helpers/SocketJsonMessageAwaiter.py
ADD src/helpers/SynchronizedDict.py src/helpers/SynchronizedDict.py

ADD src/model/AwaitableResult.py src/model/AwaitableResult.py

ADD src/presentation/song_adder src/presentation/song_adder
ADD src/presentation/abstract_classes/AbstractFastApiController.py src/presentation/abstract_classes/AbstractFastApiController.py
ADD src/presentation/abstract_classes/routes/AbstractSecuredRoutable.py src/presentation/abstract_classes/routes/AbstractSecuredRoutable.py

ENTRYPOINT ["python3", "main.py"]