"""콘솔 출력 포맷터 (MonitorFormatter)

모든 메서드는 str을 반환하며, 내부에서 print()를 호출하지 않는다.
호출자(main.py 또는 Controller)가 반환된 문자열을 print()로 출력한다.
"""
from app.model.enums import OrderStatus
from app.monitor.aggregator import StockLevel, StockStatus, ProductionSummary

# 컬럼 너비 상수
COL_W_SAMPLE = 22
COL_W_STOCK = 10
COL_W_LEVEL = 8
COL_W_RATIO = 6
COL_W_STATUS = 14
COL_W_COUNT = 5
COL_W_ORDER_NO = 12
COL_W_QTY = 10
COL_W_TIME = 12

# 상태 표시 레이블
STATUS_LABELS = {
    OrderStatus.RESERVED: "RESERVED",
    OrderStatus.CONFIRMED: "CONFIRMED",
    OrderStatus.PRODUCING: "PRODUCING",
    OrderStatus.RELEASE: "RELEASE",
}


class MonitorFormatter:

    def format_order_summary(self, counts: dict[OrderStatus, int]) -> str:
        """상태별 주문 현황 테이블 문자열 반환."""
        lines = [
            "=" * 30,
            "  상태별 주문 현황",
            "=" * 30,
        ]
        for status in [OrderStatus.RESERVED, OrderStatus.CONFIRMED, OrderStatus.PRODUCING, OrderStatus.RELEASE]:
            label = STATUS_LABELS[status]
            count = counts.get(status, 0)
            lines.append(f"  {label:<{COL_W_STATUS}}{count:>{COL_W_COUNT}}건")
        lines.append("=" * 30)
        return "\n".join(lines)

    def format_stock_summary(self, stock_list: list[StockStatus]) -> str:
        """시료별 재고 현황 테이블 문자열 반환."""
        header = self._make_table_header(
            ["시료명", "재고", "상태", "잔여율"],
            [COL_W_SAMPLE, COL_W_STOCK, COL_W_LEVEL, COL_W_RATIO],
        )
        lines = [header]
        lines.append("-" * (COL_W_SAMPLE + COL_W_STOCK + COL_W_LEVEL + COL_W_RATIO + 6))
        for ss in stock_list:
            ratio_pct = int(ss.remaining_ratio * 100)
            stock_str = f"{ss.sample.stock} ea"
            level_str = ss.level.value
            ratio_str = f"{ratio_pct}%"
            lines.append(
                f"  {ss.sample.name:<{COL_W_SAMPLE}}"
                f"{stock_str:>{COL_W_STOCK}}"
                f"   {level_str:<{COL_W_LEVEL}}"
                f"{ratio_str:>{COL_W_RATIO}}"
            )
        return "\n".join(lines)

    def format_production_queue(self, queue: list[ProductionSummary]) -> str:
        """생산 대기 목록 테이블 문자열 반환 (FIFO 순)."""
        header = self._make_table_header(
            ["주문번호", "시료명", "주문량", "부족량", "실생산량", "예상시간(분)"],
            [COL_W_ORDER_NO, COL_W_SAMPLE, COL_W_QTY, COL_W_QTY, COL_W_QTY, COL_W_TIME],
        )
        lines = [header]
        sep_width = COL_W_ORDER_NO + COL_W_SAMPLE + COL_W_QTY * 3 + COL_W_TIME + 8
        lines.append("-" * sep_width)
        for ps in queue:
            lines.append(
                f"  {ps.order_no:<{COL_W_ORDER_NO}}"
                f"{ps.sample_name:<{COL_W_SAMPLE}}"
                f"{ps.order_qty:>{COL_W_QTY}}"
                f"{ps.shortage:>{COL_W_QTY}}"
                f"{ps.actual_qty:>{COL_W_QTY}}"
                f"{ps.total_time:>{COL_W_TIME}.1f}"
            )
        return "\n".join(lines)

    def format_main_dashboard(
        self,
        counts: dict[OrderStatus, int],
        stock_list: list[StockStatus],
    ) -> str:
        """메인 화면용 요약 한 줄 반환."""
        sample_count = len(stock_list)
        total_stock = sum(ss.sample.stock for ss in stock_list)
        total_orders = sum(counts.values())
        producing_count = counts.get(OrderStatus.PRODUCING, 0)
        return (
            f"등록 시료 {sample_count}종 / "
            f"총 재고 {total_stock:,} ea / "
            f"전체 주문 {total_orders}건 / "
            f"생산라인 {producing_count}건 대기"
        )

    # ------------------------------------------------------------------ #
    # 내부 헬퍼                                                           #
    # ------------------------------------------------------------------ #

    def _make_table_header(self, col_names: list[str], widths: list[int]) -> str:
        """공통 테이블 헤더 문자열 생성."""
        parts = ["  "]
        for name, w in zip(col_names, widths):
            parts.append(f"{name:<{w}}")
        return "".join(parts)
