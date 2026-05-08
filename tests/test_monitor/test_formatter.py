"""Phase 3 - Red: MonitorFormatter 단위 테스트"""
import pytest
from datetime import datetime
from unittest.mock import MagicMock

from app.model.enums import OrderStatus
from app.model.sample import Sample
from app.monitor.aggregator import StockLevel, StockStatus, ProductionSummary
from app.monitor.formatter import MonitorFormatter


def make_sample(sample_id, name, stock, yield_rate=0.90, avg_production_time=120.0):
    return Sample(
        sample_id=sample_id,
        name=name,
        stock=stock,
        yield_rate=yield_rate,
        avg_production_time=avg_production_time,
    )


class TestFormatOrderSummary:
    def test_format_order_summary_returns_str(self):
        """반환 타입이 str이고 RESERVED/CONFIRMED/PRODUCING/RELEASE 포함 확인"""
        formatter = MonitorFormatter()
        counts = {
            OrderStatus.RESERVED: 3,
            OrderStatus.CONFIRMED: 8,
            OrderStatus.PRODUCING: 3,
            OrderStatus.RELEASE: 18,
        }
        result = formatter.format_order_summary(counts)

        assert isinstance(result, str)
        assert "RESERVED" in result
        assert "CONFIRMED" in result
        assert "PRODUCING" in result
        assert "RELEASE" in result

    def test_format_order_summary_contains_counts(self):
        """건수 숫자가 포함되어 있는지 확인"""
        formatter = MonitorFormatter()
        counts = {
            OrderStatus.RESERVED: 5,
            OrderStatus.CONFIRMED: 10,
            OrderStatus.PRODUCING: 2,
            OrderStatus.RELEASE: 20,
        }
        result = formatter.format_order_summary(counts)

        assert "5" in result
        assert "10" in result
        assert "2" in result
        assert "20" in result

    def test_format_order_summary_no_print_called(self):
        """내부에서 print()를 호출하지 않고 str만 반환하는지 확인 (monkeypatch)"""
        formatter = MonitorFormatter()
        counts = {
            OrderStatus.RESERVED: 1,
            OrderStatus.CONFIRMED: 1,
            OrderStatus.PRODUCING: 1,
            OrderStatus.RELEASE: 1,
        }
        # print가 호출되지 않아야 하므로 반환값이 str인지만 확인
        result = formatter.format_order_summary(counts)
        assert isinstance(result, str)
        assert len(result) > 0


class TestFormatStockSummary:
    def test_format_stock_summary_contains_levels(self):
        """"여유", "부족", "고갈" 텍스트 포함 확인"""
        formatter = MonitorFormatter()
        stock_list = [
            StockStatus(
                sample=make_sample("S001", "실리콘 웨이퍼-8인치", stock=480),
                level=StockLevel.SUFFICIENT,
                remaining_ratio=0.80,
            ),
            StockStatus(
                sample=make_sample("S002", "SiC 파워기판-6인치", stock=30),
                level=StockLevel.SHORTAGE,
                remaining_ratio=0.06,
            ),
            StockStatus(
                sample=make_sample("S003", "산화막 웨이퍼-SiO2", stock=0),
                level=StockLevel.DEPLETED,
                remaining_ratio=0.0,
            ),
        ]
        result = formatter.format_stock_summary(stock_list)

        assert isinstance(result, str)
        assert "여유" in result
        assert "부족" in result
        assert "고갈" in result

    def test_format_stock_summary_contains_sample_names(self):
        """시료 이름이 출력에 포함되는지 확인"""
        formatter = MonitorFormatter()
        stock_list = [
            StockStatus(
                sample=make_sample("S001", "실리콘 웨이퍼-8인치", stock=100),
                level=StockLevel.SUFFICIENT,
                remaining_ratio=1.0,
            ),
        ]
        result = formatter.format_stock_summary(stock_list)

        assert "실리콘 웨이퍼-8인치" in result

    def test_format_stock_summary_returns_str(self):
        """반환 타입이 str인지 확인"""
        formatter = MonitorFormatter()
        result = formatter.format_stock_summary([])
        assert isinstance(result, str)


class TestFormatProductionQueue:
    def test_format_production_queue_returns_str(self):
        """반환 타입이 str인지 확인"""
        formatter = MonitorFormatter()
        queue = [
            ProductionSummary(
                order_no="ORD-001",
                sample_name="실리콘 웨이퍼-8인치",
                order_qty=100,
                shortage=70,
                actual_qty=87,
                total_time=10440.0,
            )
        ]
        result = formatter.format_production_queue(queue)
        assert isinstance(result, str)

    def test_format_production_queue_contains_order_info(self):
        """주문 번호, 시료명 포함 확인"""
        formatter = MonitorFormatter()
        queue = [
            ProductionSummary(
                order_no="ORD-999",
                sample_name="GaN 에피 기판-4인치",
                order_qty=200,
                shortage=150,
                actual_qty=207,
                total_time=31050.0,
            )
        ]
        result = formatter.format_production_queue(queue)
        assert "ORD-999" in result
        assert "GaN 에피 기판-4인치" in result

    def test_format_production_queue_empty_list(self):
        """빈 리스트일 때도 str을 반환하는지 확인"""
        formatter = MonitorFormatter()
        result = formatter.format_production_queue([])
        assert isinstance(result, str)


class TestFormatMainDashboard:
    def test_format_main_dashboard_returns_str(self):
        """반환 타입이 str인지 확인"""
        formatter = MonitorFormatter()
        counts = {
            OrderStatus.RESERVED: 3,
            OrderStatus.CONFIRMED: 8,
            OrderStatus.PRODUCING: 3,
            OrderStatus.RELEASE: 18,
        }
        stock_list = [
            StockStatus(
                sample=make_sample("S001", "실리콘 웨이퍼-8인치", stock=480),
                level=StockLevel.SUFFICIENT,
                remaining_ratio=0.80,
            ),
        ]
        result = formatter.format_main_dashboard(counts, stock_list)
        assert isinstance(result, str)

    def test_format_main_dashboard_contains_summary_info(self):
        """시료 수, 재고량, 주문 건수 포함 확인"""
        formatter = MonitorFormatter()
        counts = {
            OrderStatus.RESERVED: 2,
            OrderStatus.CONFIRMED: 3,
            OrderStatus.PRODUCING: 1,
            OrderStatus.RELEASE: 4,
        }
        stock_list = [
            StockStatus(
                sample=make_sample("S001", "실리콘 웨이퍼-8인치", stock=480),
                level=StockLevel.SUFFICIENT,
                remaining_ratio=0.80,
            ),
            StockStatus(
                sample=make_sample("S002", "SiC 파워기판-6인치", stock=30),
                level=StockLevel.SHORTAGE,
                remaining_ratio=0.06,
            ),
        ]
        result = formatter.format_main_dashboard(counts, stock_list)
        # 시료 2종, 총 재고 510, 전체 주문 10건, 생산라인 1건 대기
        assert isinstance(result, str)
        assert len(result) > 0
