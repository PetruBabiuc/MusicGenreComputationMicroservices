FROM python:3.9-alpine

ENV PYTHONUNBUFFERED=1
ENV IMAGE_PATH=docker_images/api/crawler_management_controller

ADD $IMAGE_PATH/requirements.txt requirements.txt
RUN pip install -r requirements.txt
ADD $IMAGE_PATH/main.py /main.py

ADD config/crawler_engine.py /config/crawler_engine.py
ADD config/crawler_management_controller.py /config/crawler_management_controller.py
ADD config/database_api_credentials.py /config/database_api_credentials.py
ADD config/database_api.py /config/database_api.py
ADD config/front_end.py /config/front_end.py
ADD config/jwt.py /config/jwt.py
ADD config/user_types.py /config/user_types.py

ADD src/helpers/Base64Converter.py /src/helpers/Base64Converter.py
ADD src/helpers/DatabaseApiProxy.py /src/helpers/DatabaseApiProxy.py
ADD src/helpers/HighLevelSocketWrapper.py /src/helpers/HighLevelSocketWrapper.py
ADD src/helpers/SocketJsonMessageAwaiter.py /src/helpers/SocketJsonMessageAwaiter.py
ADD src/helpers/SynchronizedDict.py /src/helpers/SynchronizedDict.py
ADD src/helpers/SynchronizedSet.py /src/helpers/SynchronizedSet.py

ADD src/helpers/abstract_classes/AbstractMessageAwaiter.py /src/helpers/abstract_classes/AbstractMessageAwaiter.py
ADD src/helpers/abstract_classes/MessageProducerInterface.py /src/helpers/abstract_classes/MessageProducerInterface.py
ADD src/helpers/abstract_classes/SyncMessageConsumerInterface.py /src/helpers/abstract_classes/SyncMessageConsumerInterface.py

ADD src/helpers/security/FastApiJwtManager.py /src/helpers/security/FastApiJwtManager.py
ADD src/helpers/security/JwtManager.py /src/helpers/security/JwtManager.py

ADD src/model/AwaitableResult.py /src/model/AwaitableResult.py
ADD src/model/dto/StartCrawlingRequest.py /src/model/dto/StartCrawlingRequest.py

ADD src/presentation/abstract_classes/AbstractFastApiController.py src/presentation/abstract_classes/AbstractFastApiController.py
ADD src/presentation/abstract_classes/routes/AbstractSecuredRoutable.py src/presentation/abstract_classes/routes/AbstractSecuredRoutable.py

ADD src/presentation/crawler_management/CrawlerManagementController.py /src/presentation/crawler_management/CrawlerManagementController.py
ADD src/presentation/crawler_management/routes /src/presentation/crawler_management/routes

ADD src/AbstractMicroservice.py /src/AbstractMicroservice.py

ENTRYPOINT ["python3", "main.py"]