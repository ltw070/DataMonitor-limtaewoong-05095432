"""데이터 집계 로직 (MonitorAggregator)"""
import math
from dataclasses import dataclass
from enum import Enum

from app.model.enums import OrderStatus
from app.model.sample import Sample
from app.repository.sample_repository import SampleRepository
from app.repository.order_repository import OrderRepository

# 수율 보정 계수
YIELD_CORRECTION_FACTOR = 0.9

# 집계 대상 주문 상태 (REJECTED 제외)
COUNTED_STATUSES = [
    OrderStatus.RESERVED,
    OrderStatus.CONFIRMED,
    OrderStatus.PRODUCING,
    OrderStatus.RELEASE,
]

# 활성 주문 상태 (재고 판단 기준)
ACTIVE_STATUSES = [OrderStatus.CONFIRMED, OrderStatus.PRODUCING]


class StockLevel(Enum):
    SUFFICIENT = "여유"
    SHORTAGE = "부족"
    DEPLETED = "고갈"


@dataclass
class StockStatus:
    sample: Sample
    level: StockLevel
    remaining_ratio: float  # stock / (총 CONFIRMED+PRODUCING 주문량), 0~1


@dataclass
class ProductionSummary:
    order_no: str
    sample_name: str
    order_qty: int
    shortage: int
    actual_qty: int    # ceil(shortage / (yield_rate * YIELD_CORRECTION_FACTOR))
    total_time: float  # avg_production_time * actual_qty (분)


class MonitorAggregator:
    def __init__(self, sample_repo: SampleRepository, order_repo: OrderRepository):
        self._sample_repo = sample_repo
        self._order_repo = order_repo

    def order_counts_by_status(self) -> dict[OrderStatus, int]:
        """RESERVED / CONFIRMED / PRODUCING / RELEASE 건수 반환. REJECTED 제외."""
        counts = {status: 0 for status in COUNTED_STATUSES}
        for order in self._order_repo.find_all():
            if order.status in counts:
                counts[order.status] += 1
        return counts

    def stock_status_by_sample(self) -> list[StockStatus]:
        """시료별 재고 현황 반환."""
        all_orders = self._order_repo.find_all()
        result = []
        for sample in self._sample_repo.find_all():
            active_qty = self._calc_active_order_qty(sample.sample_id, all_orders)
            level = self._determine_stock_level(sample.stock, active_qty)
            remaining_ratio = self._calc_remaining_ratio(sample.stock, active_qty)
            result.append(StockStatus(
                sample=sample,
                level=level,
                remaining_ratio=remaining_ratio,
            ))
        return result

    def production_queue_summary(self) -> list[ProductionSummary]:
        """PRODUCING 상태 주문의 생산 정보 요약 (FIFO 순)."""
        all_orders = self._order_repo.find_all()
        producing_orders = sorted(
            [o for o in all_orders if o.status == OrderStatus.PRODUCING],
            key=lambda o: o.created_at,
        )
        result = []
        for order in producing_orders:
            sample = self._sample_repo.find_by_id(order.sample_id)
            if sample is None:
                continue
            shortage = max(0, order.order_qty - sample.stock)
            actual_qty = math.ceil(shortage / (sample.yield_rate * YIELD_CORRECTION_FACTOR))
            total_time = sample.avg_production_time * actual_qty
            result.append(ProductionSummary(
                order_no=order.order_no,
                sample_name=sample.name,
                order_qty=order.order_qty,
                shortage=shortage,
                actual_qty=actual_qty,
                total_time=total_time,
            ))
        return result

    def _calc_active_order_qty(self, sample_id: str, all_orders) -> int:
        """특정 시료의 활성 주문(CONFIRMED+PRODUCING) 총 주문량 계산."""
        return sum(
            o.order_qty
            for o in all_orders
            if o.sample_id == sample_id and o.status in ACTIVE_STATUSES
        )

    def _determine_stock_level(self, stock: int, active_qty: int) -> StockLevel:
        """재고 수량과 활성 주문량을 비교해 StockLevel 반환."""
        if stock == 0:
            return StockLevel.DEPLETED
        if stock < active_qty:
            return StockLevel.SHORTAGE
        return StockLevel.SUFFICIENT

    def _calc_remaining_ratio(self, stock: int, active_qty: int) -> float:
        """잔여율 계산: stock / active_qty. 활성 주문 없으면 1.0."""
        if active_qty == 0:
            return 1.0
        return stock / active_qty
