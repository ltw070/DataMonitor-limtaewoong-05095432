"""제네릭 Repository ABC 인터페이스"""
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional

T = TypeVar("T")


class BaseRepository(ABC, Generic[T]):
    @abstractmethod
    def find_by_id(self, id: str) -> Optional[T]:
        raise NotImplementedError

    @abstractmethod
    def find_all(self) -> list[T]:
        raise NotImplementedError

    @abstractmethod
    def save(self, entity: T) -> T:
        raise NotImplementedError

    @abstractmethod
    def delete(self, id: str) -> bool:
        raise NotImplementedError
