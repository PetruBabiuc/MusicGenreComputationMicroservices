import heapq
import time
from datetime import datetime
from http import HTTPStatus
from threading import Lock
from typing import Any

from fastapi import HTTPException

from config.jwt import JWT_MAX_AGE_MINUTES
from src.helpers.abstract_classes.JwtBlacklistInterface import JwtBlacklistInterface
from src.helpers.security.FastApiJwtManager import FastApiJwtManager


class BlacklistFastApiJwtManager(JwtBlacklistInterface, FastApiJwtManager):
    def __init__(self) -> None:
        super().__init__()
        self.__lock = Lock()
        self.__jwt_set = set()
        self.__exp_to_jwt_minheap = []
        self.__log_func = lambda s: print(f'[JwtBlacklistCleanerThread] {s}')
        self.__seconds_delta = 1

    def blacklist_jwt(self, jwt: str, exp: int) -> None:
        with self.__lock:
            self.__jwt_set.add(jwt)
            heapq.heappush(self.__exp_to_jwt_minheap, (exp, jwt))

    def is_jwt_blacklisted(self, jwt: str) -> bool:
        with self.__lock:
            return jwt in self.__jwt_set

    def decode_jwt(self, encoded_jwt: str) -> dict[str, Any]:
        if self.is_jwt_blacklisted(encoded_jwt):
            raise HTTPException(HTTPStatus.FORBIDDEN)

        return super().decode_jwt(encoded_jwt)

    def __get_sleep_time(self, exp: int) -> float:
        return max(exp - datetime.now().timestamp() + self.__seconds_delta, self.__seconds_delta)

    def start_blacklist_cleaning(self) -> None:
        self.__log_func('Started cleaning the JWT blacklist...')
        while True:
            with self.__lock:
                # If no blacklisted JWT sleep the max age of a JWT
                if len(self.__exp_to_jwt_minheap) == 0:
                    sleep_time = JWT_MAX_AGE_MINUTES * 60
                    self.__log_func('Cleaned nothing...')
                else:
                    # Any blacklisted JWT
                    exp, jwt = self.__exp_to_jwt_minheap[0]

                    # If the JWT is expired then it, from now on, will be rejected
                    # because of its 'exp' field, so we can remove it from the blacklist
                    if exp < int(datetime.now().timestamp()):
                        self.__jwt_set.remove(jwt)
                        heapq.heappop(self.__exp_to_jwt_minheap)
                        self.__log_func(f'Cleaned JWT: {jwt}')

                        # If there is no other blacklisted JWT the thread sleep the max
                        # age of a JWT
                        if len(self.__exp_to_jwt_minheap) == 0:
                            sleep_time = JWT_MAX_AGE_MINUTES * 60

                        # If there is any blacklisted JWT left the thread sleeps and
                        # wakes up as soon as any JWT expires
                        else:
                            exp, _ = self.__exp_to_jwt_minheap[0]
                            sleep_time = self.__get_sleep_time(exp)

                    # The first-to-expire JWT is not expired so the thread sleeps until it expire
                    else:
                        self.__log_func('Cleaned nothing...')
                        sleep_time = self.__get_sleep_time(exp)

            self.__log_func(f'Sleeping {sleep_time} seconds...')
            time.sleep(sleep_time)
