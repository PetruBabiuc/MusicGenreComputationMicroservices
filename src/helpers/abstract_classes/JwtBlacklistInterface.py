from abc import ABCMeta, abstractmethod


class JwtBlacklistInterface(metaclass=ABCMeta):
    @abstractmethod
    def blacklist_jwt(self, jwt: str, exp: int) -> None:
        pass

    @abstractmethod
    def is_jwt_blacklisted(self, jwt: str) -> bool:
        pass
