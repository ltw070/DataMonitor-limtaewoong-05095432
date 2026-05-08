"""SampleRepository ABC 인터페이스"""
from abc import abstractmethod
from typing import Optional
from app.model.sample import Sample
from app.repository.base_repository import BaseRepository


class SampleRepository(BaseRepository[Sample]):
    @abstractmethod
    def find_by_id(self, sample_id: str) -> Optional[Sample]:
        raise NotImplementedError

    @abstractmethod
    def find_all(self) -> list[Sample]:
        raise NotImplementedError

    @abstractmethod
    def save(self, sample: Sample) -> Sample:
        raise NotImplementedError

    @abstractmethod
    def delete(self, sample_id: str) -> bool:
        raise NotImplementedError
