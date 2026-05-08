"""주문(Order) 도메인 모델"""
from dataclasses import dataclass
from datetime import datetime
from app.model.enums import OrderStatus


@dataclass
class Order:
    order_no: str
    sample_id: str
    order_qty: int
    status: OrderStatus
    created_at: datetime
