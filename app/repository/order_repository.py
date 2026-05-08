"""OrderRepository ABC 인터페이스"""
from abc import abstractmethod
from typing import Optional
from app.model.order import Order
from app.model.enums import OrderStatus
from app.repository.base_repository import BaseRepository


class OrderRepository(BaseRepository[Order]):
    @abstractmethod
    def find_by_id(self, order_no: str) -> Optional[Order]:
        raise NotImplementedError

    @abstractmethod
    def find_all(self) -> list[Order]:
        raise NotImplementedError

    @abstractmethod
    def find_by_status(self, status: OrderStatus) -> list[Order]:
        raise NotImplementedError

    @abstractmethod
    def find_by_sample_id(self, sample_id: str) -> list[Order]:
        raise NotImplementedError

    @abstractmethod
    def save(self, order: Order) -> Order:
        raise NotImplementedError

    @abstractmethod
    def delete(self, order_no: str) -> bool:
        raise NotImplementedError
