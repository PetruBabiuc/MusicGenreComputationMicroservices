from passlib.context import CryptContext


class PasswordManager:
    def __init__(self):
        self.__password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def hash_password(self, password: str) -> str:
        return self.__password_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.__password_context.verify(plain_password, hashed_password)
