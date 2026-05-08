"""Phase 2 - Red: Aggregator 단위 테스트 (MagicMock으로 Repository 격리)"""
import math
import pytest
from datetime import datetime
from unittest.mock import MagicMock

from app.model.enums import OrderStatus
from app.model.sample import Sample
from app.model.order import Order
from app.monitor.aggregator import MonitorAggregator, StockLevel, StockStatus, ProductionSummary


def make_order(order_no, sample_id, qty, status):
    return Order(
        order_no=order_no,
        sample_id=sample_id,
        order_qty=qty,
        status=status,
        created_at=datetime(2026, 1, 1, 9, 0, 0),
    )


def make_sample(sample_id, name, stock, yield_rate=0.90, avg_production_time=120.0):
    return Sample(
        sample_id=sample_id,
        name=name,
        stock=stock,
        yield_rate=yield_rate,
        avg_production_time=avg_production_time,
    )


class TestOrderCountsByStatus:
    def test_order_counts_excludes_rejected(self):
        """REJECTED 주문이 집계에서 제외되는지 확인"""
        sample_repo = MagicMock()
        order_repo = MagicMock()

        orders = [
            make_order("ORD-001", "S001", 10, OrderStatus.RESERVED),
            make_order("ORD-002", "S001", 20, OrderStatus.CONFIRMED),
            make_order("ORD-003", "S001", 30, OrderStatus.REJECTED),
            make_order("ORD-004", "S001", 40, OrderStatus.PRODUCING),
        ]
        order_repo.find_all.return_value = orders

        aggregator = MonitorAggregator(sample_repo, order_repo)
        counts = aggregator.order_counts_by_status()

        assert OrderStatus.REJECTED not in counts

    def test_order_counts_by_status(self):
        """각 상태별 건수가 정확한지 확인"""
        sample_repo = MagicMock()
        order_repo = MagicMock()

        orders = [
            make_order("ORD-001", "S001", 10, OrderStatus.RESERVED),
            make_order("ORD-002", "S001", 20, OrderStatus.RESERVED),
            make_order("ORD-003", "S001", 30, OrderStatus.CONFIRMED),
            make_order("ORD-004", "S001", 40, OrderStatus.CONFIRMED),
            make_order("ORD-005", "S001", 50, OrderStatus.CONFIRMED),
            make_order("ORD-006", "S001", 60, OrderStatus.PRODUCING),
            make_order("ORD-007", "S001", 70, OrderStatus.RELEASE),
            make_order("ORD-008", "S001", 80, OrderStatus.RELEASE),
            make_order("ORD-009", "S001", 90, OrderStatus.REJECTED),
        ]
        order_repo.find_all.return_value = orders

        aggregator = MonitorAggregator(sample_repo, order_repo)
        counts = aggregator.order_counts_by_status()

        assert counts[OrderStatus.RESERVED] == 2
        assert counts[OrderStatus.CONFIRMED] == 3
        assert counts[OrderStatus.PRODUCING] == 1
        assert counts[OrderStatus.RELEASE] == 2

    def test_order_counts_all_statuses_present_in_result(self):
        """결과에 RESERVED/CONFIRMED/PRODUCING/RELEASE 4개 키가 존재해야 함"""
        sample_repo = MagicMock()
        order_repo = MagicMock()
        order_repo.find_all.return_value = []

        aggregator = MonitorAggregator(sample_repo, order_repo)
        counts = aggregator.order_counts_by_status()

        assert OrderStatus.RESERVED in counts
        assert OrderStatus.CONFIRMED in counts
        assert OrderStatus.PRODUCING in counts
        assert OrderStatus.RELEASE in counts


class TestStockStatus:
    def test_stock_level_depleted(self):
        """stock=0 → StockLevel.DEPLETED 반환 확인"""
        sample_repo = MagicMock()
        order_repo = MagicMock()

        sample = make_sample("S001", "실리콘 웨이퍼-8인치", stock=0)
        sample_repo.find_all.return_value = [sample]

        orders = [
            make_order("ORD-001", "S001", 100, OrderStatus.CONFIRMED),
        ]
        order_repo.find_all.return_value = orders

        aggregator = MonitorAggregator(sample_repo, order_repo)
        stock_list = aggregator.stock_status_by_sample()

        assert len(stock_list) == 1
        assert stock_list[0].level == StockLevel.DEPLETED

    def test_stock_level_shortage(self):
        """stock < 활성 주문 총 주문량 → StockLevel.SHORTAGE 반환 확인"""
        sample_repo = MagicMock()
        order_repo = MagicMock()

        sample = make_sample("S001", "실리콘 웨이퍼-8인치", stock=50)
        sample_repo.find_all.return_value = [sample]

        # CONFIRMED 60 + PRODUCING 40 = 100 > stock 50 → SHORTAGE
        orders = [
            make_order("ORD-001", "S001", 60, OrderStatus.CONFIRMED),
            make_order("ORD-002", "S001", 40, OrderStatus.PRODUCING),
            make_order("ORD-003", "S001", 30, OrderStatus.RESERVED),   # 활성 주문 제외
            make_order("ORD-004", "S001", 20, OrderStatus.RELEASE),    # 활성 주문 제외
        ]
        order_repo.find_all.return_value = orders

        aggregator = MonitorAggregator(sample_repo, order_repo)
        stock_list = aggregator.stock_status_by_sample()

        assert len(stock_list) == 1
        assert stock_list[0].level == StockLevel.SHORTAGE

    def test_stock_level_sufficient(self):
        """stock >= 활성 주문 총 주문량 → StockLevel.SUFFICIENT 반환 확인"""
        sample_repo = MagicMock()
        order_repo = MagicMock()

        sample = make_sample("S001", "실리콘 웨이퍼-8인치", stock=200)
        sample_repo.find_all.return_value = [sample]

        # CONFIRMED 80 + PRODUCING 20 = 100 <= stock 200 → SUFFICIENT
        orders = [
            make_order("ORD-001", "S001", 80, OrderStatus.CONFIRMED),
            make_order("ORD-002", "S001", 20, OrderStatus.PRODUCING),
        ]
        order_repo.find_all.return_value = orders

        aggregator = MonitorAggregator(sample_repo, order_repo)
        stock_list = aggregator.stock_status_by_sample()

        assert len(stock_list) == 1
        assert stock_list[0].level == StockLevel.SUFFICIENT

    def test_stock_level_sufficient_when_no_active_orders(self):
        """활성 주문이 없으면 재고가 있을 때 SUFFICIENT"""
        sample_repo = MagicMock()
        order_repo = MagicMock()

        sample = make_sample("S001", "실리콘 웨이퍼-8인치", stock=100)
        sample_repo.find_all.return_value = [sample]
        order_repo.find_all.return_value = []

        aggregator = MonitorAggregator(sample_repo, order_repo)
        stock_list = aggregator.stock_status_by_sample()

        assert stock_list[0].level == StockLevel.SUFFICIENT

    def test_remaining_ratio_calculation(self):
        """remaining_ratio = stock / 총 활성 주문량"""
        sample_repo = MagicMock()
        order_repo = MagicMock()

        sample = make_sample("S001", "실리콘 웨이퍼-8인치", stock=80)
        sample_repo.find_all.return_value = [sample]

        orders = [
            make_order("ORD-001", "S001", 80, OrderStatus.CONFIRMED),
            make_order("ORD-002", "S001", 20, OrderStatus.PRODUCING),
        ]
        order_repo.find_all.return_value = orders

        aggregator = MonitorAggregator(sample_repo, order_repo)
        stock_list = aggregator.stock_status_by_sample()

        # 80 / 100 = 0.8
        assert abs(stock_list[0].remaining_ratio - 0.8) < 1e-9


class TestProductionSummary:
    def test_production_summary_calc(self):
        """actual_qty = ceil(shortage / (yield_rate * 0.9)) 계산 정확성 확인"""
        sample_repo = MagicMock()
        order_repo = MagicMock()

        # yield_rate=0.90, avg_production_time=120
        sample = make_sample("S001", "실리콘 웨이퍼-8인치", stock=30, yield_rate=0.90, avg_production_time=120.0)
        sample_repo.find_all.return_value = [sample]
        sample_repo.find_by_id.return_value = sample

        # PRODUCING 주문 하나, order_qty=100
        orders = [
            make_order("ORD-001", "S001", 100, OrderStatus.PRODUCING),
        ]
        order_repo.find_all.return_value = orders

        aggregator = MonitorAggregator(sample_repo, order_repo)
        summaries = aggregator.production_queue_summary()

        assert len(summaries) == 1
        s = summaries[0]
        assert s.order_no == "ORD-001"
        assert s.sample_name == "실리콘 웨이퍼-8인치"
        assert s.order_qty == 100

        # shortage = max(0, 100 - 30) = 70
        assert s.shortage == 70

        # actual_qty = ceil(70 / (0.90 * 0.9)) = ceil(70 / 0.81) = ceil(86.419...) = 87
        expected_actual_qty = math.ceil(70 / (0.90 * 0.9))
        assert s.actual_qty == expected_actual_qty

        # total_time = 120.0 * 87 = 10440.0
        expected_total_time = 120.0 * expected_actual_qty
        assert abs(s.total_time - expected_total_time) < 1e-6

    def test_production_queue_fifo_order(self):
        """PRODUCING 주문은 FIFO(created_at 오름차순) 순으로 반환"""
        sample_repo = MagicMock()
        order_repo = MagicMock()

        sample = make_sample("S001", "실리콘 웨이퍼-8인치", stock=0, yield_rate=0.90, avg_production_time=60.0)
        sample_repo.find_all.return_value = [sample]
        sample_repo.find_by_id.return_value = sample

        orders = [
            Order("ORD-003", "S001", 50, OrderStatus.PRODUCING, datetime(2026, 1, 3)),
            Order("ORD-001", "S001", 30, OrderStatus.PRODUCING, datetime(2026, 1, 1)),
            Order("ORD-002", "S001", 40, OrderStatus.PRODUCING, datetime(2026, 1, 2)),
        ]
        order_repo.find_all.return_value = orders

        aggregator = MonitorAggregator(sample_repo, order_repo)
        summaries = aggregator.production_queue_summary()

        assert summaries[0].order_no == "ORD-001"
        assert summaries[1].order_no == "ORD-002"
        assert summaries[2].order_no == "ORD-003"

    def test_production_queue_excludes_non_producing(self):
        """PRODUCING 이외 상태 주문은 생산 대기 목록에 포함되지 않음"""
        sample_repo = MagicMock()
        order_repo = MagicMock()

        sample = make_sample("S001", "실리콘 웨이퍼-8인치", stock=100)
        sample_repo.find_all.return_value = [sample]
        sample_repo.find_by_id.return_value = sample

        orders = [
            make_order("ORD-001", "S001", 50, OrderStatus.RESERVED),
            make_order("ORD-002", "S001", 60, OrderStatus.CONFIRMED),
            make_order("ORD-003", "S001", 70, OrderStatus.PRODUCING),
            make_order("ORD-004", "S001", 80, OrderStatus.RELEASE),
            make_order("ORD-005", "S001", 90, OrderStatus.REJECTED),
        ]
        order_repo.find_all.return_value = orders

        aggregator = MonitorAggregator(sample_repo, order_repo)
        summaries = aggregator.production_queue_summary()

        assert len(summaries) == 1
        assert summaries[0].order_no == "ORD-003"

    def test_production_queue_skips_order_when_sample_not_found(self):
        """find_by_id가 None을 반환하면 해당 주문을 건너뜀"""
        sample_repo = MagicMock()
        order_repo = MagicMock()

        sample_repo.find_by_id.return_value = None  # 시료 없음
        orders = [
            make_order("ORD-001", "S999", 50, OrderStatus.PRODUCING),
        ]
        order_repo.find_all.return_value = orders

        aggregator = MonitorAggregator(sample_repo, order_repo)
        summaries = aggregator.production_queue_summary()

        assert len(summaries) == 0
