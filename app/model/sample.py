"""시료(Sample) 도메인 모델"""
from dataclasses import dataclass


@dataclass
class Sample:
    sample_id: str
    name: str
    stock: int
    yield_rate: float
    avg_production_time: float
