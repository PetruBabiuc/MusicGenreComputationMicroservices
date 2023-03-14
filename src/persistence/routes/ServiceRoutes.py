from http import HTTPStatus

from classy_fastapi import get, patch
from fastapi import Body, Depends, HTTPException
from starlette import status
from starlette.responses import Response

import config.database_api as api_paths
from config.user_types import MICROSERVICE, ADMIN, USER
from src.model.orm.Service import Service
from src.model.orm.UserToService import UserToService
from src.presentation.abstract_classes.routes.AbstractSecuredDatabaseApiRoutable import AbstractSecuredDatabaseApiRoutable


class ServiceRoutes(AbstractSecuredDatabaseApiRoutable):
    @get(api_paths.SERVICES_PATH)
    def get_all_services(self, service_name: str = None):
        session = self._create_session()
        query = session.query(Service)
        if service_name is not None:
            query = query.filter_by(service_name=service_name)
        services = query.all()
        return services

    @get(api_paths.USER_BY_ID_SERVICES_PATH)
    def get_services_of_specific_user(self, user_id: int,
                                      token: str = Depends(AbstractSecuredDatabaseApiRoutable.OAUTH2_SCHEME)):
        payload = self._jwt_manager.assert_has_user_type_in(token, [ADMIN, USER])

        if payload['user_type_id'] == USER and user_id != payload['user_id']:
            raise HTTPException(HTTPStatus.FORBIDDEN)

        session = self._create_session()
        services = session.query(UserToService).filter_by(user_id=user_id).all()

        return services

    @get(api_paths.USER_BY_ID_SERVICE_BY_ID_PATH)
    def get_specific_service_of_specific_user(self, user_id: int, service_id: int,
                                              token: str = Depends(AbstractSecuredDatabaseApiRoutable.OAUTH2_SCHEME)):
        payload = self._jwt_manager.assert_has_user_type_in(token, [MICROSERVICE, ADMIN, USER])
        if payload['user_type_id'] == USER and user_id != payload['user_id']:
            raise HTTPException(HTTPStatus.FORBIDDEN)

        session = self._create_session()
        service = session.get(UserToService, (user_id, service_id))
        if service is None:
            raise HTTPException(HTTPStatus.NOT_FOUND)
        return service

    @patch(api_paths.USER_BY_ID_SERVICE_BY_ID_PATH)
    def patch_specific_service_of_specific_user(self, user_id: int, service_id: int, body: dict = Body(),
                                                token: str = Depends(AbstractSecuredDatabaseApiRoutable.OAUTH2_SCHEME)):
        self._jwt_manager.assert_has_user_type_in(token, [MICROSERVICE, ADMIN])

        session = self._create_session()
        service = session.get(UserToService, (user_id, service_id))
        if service is None:
            return Response(status_code=status.HTTP_404_NOT_FOUND)
        if body['op'] == 'add_quantity':
            service.quantity += body['value']
        session.commit()
