from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import Iterable

from src.helpers.abstract_classes.AbstractResourceObtainer import AbstractResourceObtainer


class AbstractMimeContentProcessor(metaclass=ABCMeta):
    def __init__(self, accepted_types: Iterable[str], resource_obtainer: AbstractResourceObtainer):
        self.__accepted_types: Iterable[str] = accepted_types
        self._resource_obtainer: AbstractResourceObtainer = resource_obtainer

    def accept_type(self, resource_type: str) -> bool:
        return resource_type in self.__accepted_types

    def accept_any_of_types(self, resource_types: Iterable[str]) -> bool:
        return any(map(lambda it: it in self.__accepted_types, resource_types))

    @abstractmethod
    def process_resource(self, resource: str, domain: str) -> tuple[list[str], bool]:
        """
        Method that extracts the resources to be added in the processing queue and if the resource should be
        forwarded to the item processors.
        :param resource: Resource's URL
        :param domain: URL's domain
        :return: Tuple: (list of strings: URLs to
        the resources, bool: if the resource should be forwarded to the item processors or not)
        """
        pass
