"""주문 상태 Enum 정의"""
from enum import Enum


class OrderStatus(Enum):
    RESERVED = "RESERVED"
    CONFIRMED = "CONFIRMED"
    PRODUCING = "PRODUCING"
    RELEASE = "RELEASE"
    REJECTED = "REJECTED"
