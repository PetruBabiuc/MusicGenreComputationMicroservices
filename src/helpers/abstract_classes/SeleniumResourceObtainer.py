from abc import ABCMeta
from time import sleep

from src.helpers.abstract_classes.AbstractResourceObtainer import AbstractResourceObtainer


class SeleniumResourceObtainer(AbstractResourceObtainer[str], metaclass=ABCMeta):
    def __init__(self, driver):
        """
        :param driver: The WebDriver used to obtain resources.
        """
        self._driver = driver

    def obtain_resource(self, url: str) -> str:
        self._driver.get(url)
        sleep(1)
        return self._driver.page_source
