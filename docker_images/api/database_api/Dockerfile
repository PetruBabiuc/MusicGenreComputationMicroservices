FROM python:3.9

ENV PYTHONUNBUFFERED=1
ENV IMAGE_PATH=docker_images/api/database_api

RUN apt-get update &&  \
    apt-get install libmariadb3 libmariadb-dev

ADD $IMAGE_PATH/requirements.txt requirements.txt
RUN pip install -r requirements.txt
ADD $IMAGE_PATH/main.py main.py

ADD config/database.py /config/database.py
ADD config/database_api.py /config/database_api.py
ADD config/front_end.py /config/front_end.py
ADD config/jwt.py /config/jwt.py
ADD config/user_types.py /config/user_types.py
ADD config/dnn.py /config/dnn.py

ADD src/helpers/security/FastApiJwtManager.py /src/helpers/security/FastApiJwtManager.py
ADD src/helpers/security/JwtManager.py /src/helpers/security/JwtManager.py
ADD src/helpers/security/PasswordManager.py /src/helpers/security/PasswordManager.py
ADD src/helpers/security/BlacklistFastApiJwtManager.py /src/helpers/security/BlacklistFastApiJwtManager.py
ADD src/helpers/abstract_classes/JwtBlacklistInterface.py /src/helpers/abstract_classes/JwtBlacklistInterface.py
ADD src/helpers/ModelUtils.py /src/helpers/ModelUtils.py

ADD src/model/orm/Bill.py /src/model/orm/Bill.py
ADD src/model/orm/CrawlerState.py /src/model/orm/CrawlerState.py
ADD src/model/orm/Service.py /src/model/orm/Service.py
ADD src/model/orm/SongGenre.py /src/model/orm/SongGenre.py
ADD src/model/orm/Song.py /src/model/orm/Song.py
ADD src/model/orm/User.py /src/model/orm/User.py
ADD src/model/orm/UserType.py /src/model/orm/UserType.py
ADD src/model/orm/BloomFilter.py /src/model/orm/BloomFilter.py
ADD src/model/orm/ResourceUrl.py /src/model/orm/ResourceUrl.py
ADD src/model/orm/SongFormat.py /src/model/orm/SongFormat.py
ADD src/model/orm/SongInfo.py /src/model/orm/SongInfo.py
ADD src/model/orm/UserToService.py /src/model/orm/UserToService.py
ADD src/model/orm/SongUrl.py /src/model/orm/SongUrl.py

ADD src/model/dto/EditSongRequest.py /src/model/dto/EditSongRequest.py

ADD src/persistence/DatabaseAPI.py /src/persistence/DatabaseAPI.py
ADD src/persistence/routes /src/persistence/routes

ADD src/presentation/abstract_classes/AbstractFastApiController.py /src/presentation/abstract_classes/AbstractFastApiController.py
ADD src/presentation/abstract_classes/routes/AbstractDatabaseApiRoutable.py /src/presentation/abstract_classes/routes/AbstractDatabaseApiRoutable.py
ADD src/presentation/abstract_classes/routes/AbstractSecuredDatabaseApiRoutable.py /src/presentation/abstract_classes/routes/AbstractSecuredDatabaseApiRoutable.py

ADD src/AbstractMicroservice.py /src/AbstractMicroservice.py

ENTRYPOINT ["python3", "main.py"]