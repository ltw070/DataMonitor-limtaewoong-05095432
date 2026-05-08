# PRD: DataMonitor (데이터 모니터링 Tool)

> **PoC 목표**: 저장된 데이터 상태를 콘솔에서 실시간 조회할 수 있는 관리자 도구를 구현한다.  
> **최종 목적지**: `mission2/SampleOrderSystem` 의 모니터링 메뉴([4] 모니터링)로 편입된다.

---

## 1. 개요

`PoC2(DataPersistence)` 의 Repository에서 데이터를 읽어, 담당자가 시스템 현황을 한눈에 파악할 수 있도록 콘솔에 출력한다.  
출력 로직은 `print()` 를 직접 호출하지 않고 문자열을 반환하는 함수로 설계하여 단위 테스트를 가능하게 한다.

---

## 2. 패키지 구조

```
03_DataMonitor/
├── app/
│   ├── model/
│   │   ├── sample.py          # PoC1과 동일한 도메인 객체
│   │   ├── order.py
│   │   └── enums.py
│   ├── repository/
│   │   ├── base_repository.py
│   │   ├── sample_repository.py
│   │   └── order_repository.py  # PoC2 인터페이스 재사용
│   └── monitor/
│       ├── aggregator.py      # 데이터 집계 로직
│       └── formatter.py       # 콘솔 출력 포맷터
├── tests/
│   ├── test_model/
│   └── test_monitor/
│       ├── test_aggregator.py
│       └── test_formatter.py
├── data/                      # 조회 대상 데이터 (.gitignore)
├── main.py                    # 모니터링 도구 실행 진입점
└── requirements.txt
```

---

## 3. 도메인 모델

PoC1 · PoC2와 동일한 모델을 사용한다. (공통 인터페이스 유지)

---

## 4. 집계 인터페이스 (Aggregator)

```python
class MonitorAggregator:

    def __init__(self, sample_repo: SampleRepository, order_repo: OrderRepository): ...

    def order_counts_by_status(self) -> dict[OrderStatus, int]:
        """
        RESERVED / CONFIRMED / PRODUCING / RELEASE 건수 반환.
        REJECTED는 제외한다.
        반환 예: {OrderStatus.RESERVED: 3, OrderStatus.CONFIRMED: 8, ...}
        """

    def stock_status_by_sample(self) -> list[StockStatus]:
        """
        시료별 재고 현황 반환.
        반환 예: [StockStatus(sample=..., level=StockLevel.SUFFICIENT, remaining_ratio=0.8), ...]
        """

    def production_queue_summary(self) -> list[ProductionSummary]:
        """
        PRODUCING 상태 주문의 생산 정보 요약 (FIFO 순).
        """
```

### 4.1 보조 데이터 클래스

```python
class StockLevel(Enum):
    SUFFICIENT = "여유"   # 주문 대비 재고 충분
    SHORTAGE   = "부족"   # 주문 대비 재고 부족
    DEPLETED   = "고갈"   # stock == 0

@dataclass
class StockStatus:
    sample: Sample
    level: StockLevel
    remaining_ratio: float   # stock / (총 CONFIRMED+PRODUCING 주문량), 0~1

@dataclass
class ProductionSummary:
    order_no: str
    sample_name: str
    order_qty: int
    shortage: int
    actual_qty: int          # ceil(shortage / (yield_rate * 0.9))
    total_time: float        # avg_production_time * actual_qty (min)
```

### 4.2 재고 상태 판단 기준

```
stock == 0                          → DEPLETED  (고갈)
stock < 활성 주문의 총 주문 수량    → SHORTAGE  (부족)
stock >= 활성 주문의 총 주문 수량   → SUFFICIENT (여유)

* 활성 주문: CONFIRMED + PRODUCING 상태 주문
```

---

## 5. 출력 포맷터 인터페이스 (Formatter)

```python
class MonitorFormatter:

    def format_order_summary(self, counts: dict[OrderStatus, int]) -> str:
        """
        상태별 주문 현황 테이블 문자열 반환.
        예:
        상태별 주문 현황
        RESERVED     3건
        CONFIRMED    8건
        PRODUCING    3건
        RELEASE     18건
        """

    def format_stock_summary(self, stock_list: list[StockStatus]) -> str:
        """
        시료별 재고 현황 테이블 문자열 반환.
        예:
        시료명                재고       상태    잔여율
        실리콘 웨이퍼-8인치   480 ea     여유     80%
        SiC 파워기판-6인치     30 ea     부족      6%
        산화막 웨이퍼-SiO2      0 ea     고갈      0%
        """

    def format_production_queue(self, queue: list[ProductionSummary]) -> str:
        """
        생산 대기 목록 테이블 문자열 반환 (FIFO 순).
        """

    def format_main_dashboard(self,
                               counts: dict[OrderStatus, int],
                               stock_list: list[StockStatus]) -> str:
        """
        메인 화면용 요약 한 줄 반환.
        예: 등록 시료 12종 / 총 재고 2,840 ea / 전체 주문 36건 / 생산라인 3건 대기
        """
```

**설계 원칙**: 모든 메서드는 `str` 을 반환하며, 내부에서 `print()` 를 호출하지 않는다.  
호출자(`main.py` 또는 Controller)가 반환된 문자열을 `print()` 로 출력한다.

---

## 6. main.py 실행 흐름

```
main.py
  ├─ [1] 주문량 확인  → aggregator.order_counts_by_status()
  │                   → formatter.format_order_summary()
  │                   → print()
  ├─ [2] 재고량 확인  → aggregator.stock_status_by_sample()
  │                   → formatter.format_stock_summary()
  │                   → print()
  └─ [0] 종료
```

---

## 7. 검증 기준 (TDD)

Repository는 `pytest-mock` 의 `MagicMock` 으로 대체하여 단위 테스트를 격리한다.

| 테스트 | 검증 내용 |
|--------|----------|
| `test_order_counts_excludes_rejected` | REJECTED 주문이 집계에서 제외되는지 확인 |
| `test_order_counts_by_status` | 각 상태별 건수가 정확한지 확인 |
| `test_stock_level_depleted` | stock=0 → DEPLETED 반환 확인 |
| `test_stock_level_shortage` | stock < 주문량 → SHORTAGE 반환 확인 |
| `test_stock_level_sufficient` | stock >= 주문량 → SUFFICIENT 반환 확인 |
| `test_production_summary_calc` | `ceil(shortage / (yield * 0.9))` 계산 정확성 확인 |
| `test_format_order_summary_returns_str` | formatter가 str을 반환하는지 확인 |
| `test_format_stock_summary_contains_levels` | 출력에 여유/부족/고갈 텍스트 포함 확인 |

커버리지 목표: **80% 이상**
