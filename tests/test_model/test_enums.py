"""Phase 1 - Red: OrderStatus Enum 멤버 존재 확인 테스트"""
import pytest
from app.model.enums import OrderStatus


class TestOrderStatus:
    def test_has_reserved(self):
        assert OrderStatus.RESERVED is not None

    def test_has_confirmed(self):
        assert OrderStatus.CONFIRMED is not None

    def test_has_producing(self):
        assert OrderStatus.PRODUCING is not None

    def test_has_release(self):
        assert OrderStatus.RELEASE is not None

    def test_has_rejected(self):
        assert OrderStatus.REJECTED is not None

    def test_all_members_count(self):
        members = list(OrderStatus)
        assert len(members) == 5

    def test_values_are_strings(self):
        for status in OrderStatus:
            assert isinstance(status.value, str)
