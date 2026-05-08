"""Phase 1 - Red: Order 도메인 모델 테스트"""
import pytest
from datetime import datetime
from app.model.order import Order
from app.model.enums import OrderStatus


class TestOrder:
    def test_create_order_with_all_fields(self):
        order = Order(
            order_no="ORD-001",
            sample_id="S001",
            order_qty=100,
            status=OrderStatus.RESERVED,
            created_at=datetime(2026, 1, 1, 9, 0, 0),
        )
        assert order.order_no == "ORD-001"
        assert order.sample_id == "S001"
        assert order.order_qty == 100
        assert order.status == OrderStatus.RESERVED
        assert order.created_at == datetime(2026, 1, 1, 9, 0, 0)

    def test_order_status_is_order_status_enum(self):
        order = Order(
            order_no="ORD-002",
            sample_id="S002",
            order_qty=50,
            status=OrderStatus.CONFIRMED,
            created_at=datetime(2026, 1, 2, 10, 0, 0),
        )
        assert isinstance(order.status, OrderStatus)

    def test_order_with_producing_status(self):
        order = Order(
            order_no="ORD-003",
            sample_id="S001",
            order_qty=200,
            status=OrderStatus.PRODUCING,
            created_at=datetime(2026, 1, 3, 11, 0, 0),
        )
        assert order.status == OrderStatus.PRODUCING

    def test_order_with_release_status(self):
        order = Order(
            order_no="ORD-004",
            sample_id="S003",
            order_qty=30,
            status=OrderStatus.RELEASE,
            created_at=datetime(2026, 1, 4, 12, 0, 0),
        )
        assert order.status == OrderStatus.RELEASE

    def test_order_with_rejected_status(self):
        order = Order(
            order_no="ORD-005",
            sample_id="S002",
            order_qty=80,
            status=OrderStatus.REJECTED,
            created_at=datetime(2026, 1, 5, 13, 0, 0),
        )
        assert order.status == OrderStatus.REJECTED

    def test_order_qty_is_int(self):
        order = Order(
            order_no="ORD-006",
            sample_id="S001",
            order_qty=150,
            status=OrderStatus.RESERVED,
            created_at=datetime(2026, 1, 6, 14, 0, 0),
        )
        assert isinstance(order.order_qty, int)
