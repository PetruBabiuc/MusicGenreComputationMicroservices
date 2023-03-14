FROM python:3.9-slim

ENV PYTHONUNBUFFERED=1
ENV IMAGE_PATH=docker_images/crawler/spider

RUN apt-get update && \
    apt-get install -y python3-dev \
    gcc \
    libc-dev

ADD $IMAGE_PATH/main.py main.py
ADD $IMAGE_PATH/requirements.txt requirements.txt

RUN pip install -r requirements.txt

ADD config/constants.py config/constants.py
ADD config/rabbit_mq.py config/rabbit_mq.py
ADD config/redis.py config/redis.py
ADD config/spider.py config/spider.py

ADD src/business/abstract_classes/AbstractMp3SpiderMicroservice.py src/business/abstract_classes/AbstractMp3SpiderMicroservice.py
ADD src/business/abstract_classes/AbstractSpiderMicroservice.py src/business/abstract_classes/AbstractSpiderMicroservice.py

ADD src/business/crawler/Mp3SpiderMicroservice.py src/business/crawler/Mp3SpiderMicroservice.py

ADD src/helpers/Base64Converter.py src/helpers/Base64Converter.py
ADD src/helpers/Mp3Spider.py src/helpers/Mp3Spider.py
ADD src/helpers/Mp3ValidatorProxy.py src/helpers/Mp3ValidatorProxy.py
ADD src/helpers/RabbitMqConsumer.py src/helpers/RabbitMqConsumer.py
ADD src/helpers/RabbitMqProducer.py src/helpers/RabbitMqProducer.py
ADD src/helpers/RedisJsonMessageAwaiter.py src/helpers/RedisJsonMessageAwaiter.py
ADD src/helpers/SynchronizedDict.py src/helpers/SynchronizedDict.py

ADD src/helpers/abstract_classes/AbstractMessageAwaiter.py src/helpers/abstract_classes/AbstractMessageAwaiter.py
ADD src/helpers/abstract_classes/AbstractMimeContentProcessor.py src/helpers/abstract_classes/AbstractMimeContentProcessor.py
ADD src/helpers/abstract_classes/AbstractRabbitMqClient.py src/helpers/abstract_classes/AbstractRabbitMqClient.py
ADD src/helpers/abstract_classes/AbstractResourceObtainer.py src/helpers/abstract_classes/AbstractResourceObtainer.py
ADD src/helpers/abstract_classes/AbstractSpider.py src/helpers/abstract_classes/AbstractSpider.py
ADD src/helpers/abstract_classes/AsyncMessageConsumerInterface.py src/helpers/abstract_classes/AsyncMessageConsumerInterface.py
ADD src/helpers/abstract_classes/MessageProducerInterface.py src/helpers/abstract_classes/MessageProducerInterface.py
ADD src/helpers/abstract_classes/Mp3ValidatorProxyInterface.py src/helpers/abstract_classes/Mp3ValidatorProxyInterface.py

ADD src/helpers/resource_obtainers/SimpleResourceObtainer.py src/helpers/resource_obtainers/SimpleResourceObtainer.py

ADD src/helpers/resource_processors/HtmlProcessor.py src/helpers/resource_processors/HtmlProcessor.py
ADD src/helpers/resource_processors/Mp3Processor.py src/helpers/resource_processors/Mp3Processor.py

ADD src/model/AwaitableResult.py src/model/AwaitableResult.py
ADD src/model/SpiderReturn.py src/model/SpiderReturn.py
ADD src/model/SpiderState.py src/model/SpiderState.py

ADD src/AbstractMicroservice.py src/AbstractMicroservice.py

ENTRYPOINT ["python3", "main.py"]