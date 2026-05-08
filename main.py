"""DataMonitor 실행 진입점

콘솔에서 현재 저장된 데이터(주문 상태, 재고 현황)를 실시간으로 조회하는 관리자 도구.
"""
from unittest.mock import MagicMock
from datetime import datetime

from app.model.enums import OrderStatus
from app.model.sample import Sample
from app.model.order import Order
from app.monitor.aggregator import MonitorAggregator
from app.monitor.formatter import MonitorFormatter


def build_demo_repos():
    """실제 파일 I/O 대신 샘플 데이터를 담은 Mock Repository를 반환한다."""
    samples = [
        Sample("S001", "실리콘 웨이퍼-8인치",  480, yield_rate=0.95, avg_production_time=120.0),
        Sample("S002", "SiC 파워기판-6인치",      30, yield_rate=0.80, avg_production_time=180.0),
        Sample("S003", "산화막 웨이퍼-SiO2",       0, yield_rate=0.75, avg_production_time=90.0),
        Sample("S004", "GaN 에피 기판-4인치",     200, yield_rate=0.88, avg_production_time=150.0),
    ]
    orders = [
        Order("ORD-001", "S001", 100, OrderStatus.RESERVED,  datetime(2026, 1, 1)),
        Order("ORD-002", "S001",  80, OrderStatus.RESERVED,  datetime(2026, 1, 2)),
        Order("ORD-003", "S001",  60, OrderStatus.CONFIRMED, datetime(2026, 1, 3)),
        Order("ORD-004", "S002", 200, OrderStatus.CONFIRMED, datetime(2026, 1, 4)),
        Order("ORD-005", "S002", 150, OrderStatus.PRODUCING, datetime(2026, 1, 5)),
        Order("ORD-006", "S003",  50, OrderStatus.PRODUCING, datetime(2026, 1, 6)),
        Order("ORD-007", "S004",  30, OrderStatus.RELEASE,   datetime(2026, 1, 7)),
        Order("ORD-008", "S001",  20, OrderStatus.RELEASE,   datetime(2026, 1, 8)),
        Order("ORD-009", "S002",  10, OrderStatus.REJECTED,  datetime(2026, 1, 9)),
    ]

    sample_repo = MagicMock()
    order_repo = MagicMock()

    sample_repo.find_all.return_value = samples
    sample_repo.find_by_id.side_effect = lambda sid: next(
        (s for s in samples if s.sample_id == sid), None
    )
    order_repo.find_all.return_value = orders

    return sample_repo, order_repo


def main():
    sample_repo, order_repo = build_demo_repos()
    aggregator = MonitorAggregator(sample_repo, order_repo)
    formatter = MonitorFormatter()

    while True:
        print("\n[DataMonitor]")
        print("[1] 주문량 확인")
        print("[2] 재고량 확인")
        print("[3] 생산 대기 목록")
        print("[0] 종료")
        choice = input("선택 > ").strip()

        if choice == "1":
            counts = aggregator.order_counts_by_status()
            print(formatter.format_order_summary(counts))

        elif choice == "2":
            stock_list = aggregator.stock_status_by_sample()
            print(formatter.format_stock_summary(stock_list))

        elif choice == "3":
            queue = aggregator.production_queue_summary()
            print(formatter.format_production_queue(queue))

        elif choice == "0":
            print("종료합니다.")
            break

        else:
            print("잘못된 입력입니다. 다시 선택해주세요.")


if __name__ == "__main__":
    main()
