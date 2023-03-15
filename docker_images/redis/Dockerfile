FROM redis:7.0.9-alpine

ENV IMAGE_PATH=docker_images/redis

ADD $IMAGE_PATH/redis.conf /usr/local/etc/redis/redis.conf

ENTRYPOINT ["redis-server", "/usr/local/etc/redis/redis.conf"]