FROM rabbitmq:3.11-management

ENV IMAGE_PATH=docker_images/rabbit_mq

ADD $IMAGE_PATH/rabbitmq.conf /etc/rabbitmq/
ADD $IMAGE_PATH/definitions.json /etc/rabbitmq/

RUN chown rabbitmq:rabbitmq /etc/rabbitmq/rabbitmq.conf /etc/rabbitmq/definitions.json

CMD ["rabbitmq-server"]