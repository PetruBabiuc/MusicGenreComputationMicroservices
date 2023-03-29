from abc import ABCMeta
from typing import Callable

import uvicorn
from classy_fastapi import Routable
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from config import front_end
from src.AbstractMicroservice import AbstractMicroservice


class AbstractFastApiController(AbstractMicroservice, metaclass=ABCMeta):
    def __init__(self, routes: list[Routable], name: str, host: str, port: int,
                 log_func: Callable[[str], None] = print):
        super().__init__(name, log_func)

        self.__host = host
        self.__port = port

        self.__app = FastAPI(title=name)

        # Adding CORS for Frontend App
        origins = [
            front_end.BASE_URL
        ]

        self.__app.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=True,
            allow_methods=['*'],
            allow_headers=['*'],
        )

        for route in routes:
            self.__app.include_router(route.router)

    def run(self) -> None:
        uvicorn.run(self.__app, host=self.__host, port=self.__port)
