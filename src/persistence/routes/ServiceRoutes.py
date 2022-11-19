from classy_fastapi import get, patch
from fastapi import Body
from starlette import status
from starlette.responses import Response

import config.database_api as api_paths
from src.model.orm.Service import Service
from src.model.orm.UserToService import UserToService
from src.persistence.routes.abstract_classes.AbstractRoutable import AbstractRoutable


class ServiceRoutes(AbstractRoutable):
    @get(api_paths.SERVICES_PATH)
    def get_all_services(self, service_name: str = None):
        session = self._create_session()
        query = session.query(Service)
        if service_name is not None:
            query = query.filter_by(service_name=service_name)
        services = query.all()
        return services

    @get(api_paths.USER_BY_ID_SERVICE_BY_ID_PATH)
    def get_specific_service_of_specific_user(self, user_id: int, service_id: int):
        session = self._create_session()
        service = session.get(UserToService, (user_id, service_id))
        if service is None:
            return Response(status_code=status.HTTP_404_NOT_FOUND)
        return service

    @patch(api_paths.USER_BY_ID_SERVICE_BY_ID_PATH)
    def patch_specific_service_of_specific_user(self, user_id: int, service_id: int, body: dict = Body()):
        session = self._create_session()
        service = session.get(UserToService, (user_id, service_id))
        if service is None:
            return Response(status_code=status.HTTP_404_NOT_FOUND)
        if body['op'] == 'add_quantity':
            service.quantity += body['value']
        session.commit()
        return Response(status_code=status.HTTP_200_OK)
