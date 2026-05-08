# PLAN: DataMonitor (데이터 모니터링 Tool)

## 목표

PoC2(DataPersistence)의 Repository에서 데이터를 읽어, 콘솔에서 시스템 현황(주문 상태, 재고 현황, 생산 대기)을 실시간으로 조회할 수 있는 관리자 도구를 구현하여 `mission2/SampleOrderSystem`의 모니터링 메뉴로 편입한다.

---

## 구현 순서 (TDD: Red → Green → Refactor)

### Phase 1 – 도메인 모델 + Repository 인터페이스

PoC1/PoC2와 동일한 인터페이스를 재사용한다.

| 단계 | 파일 | 작업 내용 |
|------|------|----------|
| Red | `tests/test_model/test_enums.py` | `OrderStatus` 멤버 존재 확인 테스트 작성 |
| Red | `tests/test_model/test_sample.py` | `Sample` 생성 및 필드 타입 확인 테스트 작성 |
| Red | `tests/test_model/test_order.py` | `Order` 생성 및 `OrderStatus` 연결 확인 테스트 작성 |
| Green | `app/model/enums.py` | `OrderStatus` Enum 구현 |
| Green | `app/model/sample.py` | `Sample` dataclass 구현 |
| Green | `app/model/order.py` | `Order` dataclass 구현 |
| Green | `app/repository/base_repository.py` | 제네릭 ABC 인터페이스 구현 |
| Green | `app/repository/sample_repository.py` | `SampleRepository` ABC 구현 |
| Green | `app/repository/order_repository.py` | `OrderRepository` ABC 구현 |
| Refactor | `app/model/`, `app/repository/` | `__init__.py` 정리, import 경로 통일 |

### Phase 2 – Aggregator 구현

`MonitorAggregator`와 보조 데이터 클래스를 구현한다. Repository는 `MagicMock`으로 격리한다.

**보조 데이터 클래스 및 재고 상태 판단 기준**

```
활성 주문 = CONFIRMED + PRODUCING 상태 주문

StockLevel.DEPLETED   → stock == 0
StockLevel.SHORTAGE   → 0 < stock < 활성 주문 총 주문량
StockLevel.SUFFICIENT → stock >= 활성 주문 총 주문량
```

**생산량 계산식**

```
shortage   = max(0, order_qty - stock)
actual_qty = ceil(shortage / (yield_rate * 0.9))
total_time = avg_production_time * actual_qty  (단위: 분)
```

| 단계 | 파일 | 작업 내용 |
|------|------|----------|
| Red | `tests/test_monitor/test_aggregator.py` | `test_order_counts_excludes_rejected`: REJECTED 주문이 집계에서 제외되는지 확인 |
| Red | `tests/test_monitor/test_aggregator.py` | `test_order_counts_by_status`: 각 상태별 건수 정확성 확인 |
| Red | `tests/test_monitor/test_aggregator.py` | `test_stock_level_depleted`: stock=0 → `DEPLETED` 반환 확인 |
| Red | `tests/test_monitor/test_aggregator.py` | `test_stock_level_shortage`: stock < 활성 주문량 → `SHORTAGE` 반환 확인 |
| Red | `tests/test_monitor/test_aggregator.py` | `test_stock_level_sufficient`: stock >= 활성 주문량 → `SUFFICIENT` 반환 확인 |
| Red | `tests/test_monitor/test_aggregator.py` | `test_production_summary_calc`: `ceil(shortage / (yield_rate * 0.9))` 계산 정확성 확인 |
| Green | `app/monitor/aggregator.py` | `StockLevel`, `StockStatus`, `ProductionSummary`, `MonitorAggregator` 구현 |
| Refactor | `app/monitor/aggregator.py` | 재고 판단 로직 메서드 분리, yield 보정계수 0.9 상수화 |

### Phase 3 – Formatter 구현

모든 메서드는 `str`을 반환하며, 내부에서 `print()`를 호출하지 않는다.

| 단계 | 파일 | 작업 내용 |
|------|------|----------|
| Red | `tests/test_monitor/test_formatter.py` | `test_format_order_summary_returns_str`: 반환 타입 str, RESERVED/CONFIRMED/PRODUCING/RELEASE 포함 확인 |
| Red | `tests/test_monitor/test_formatter.py` | `test_format_stock_summary_contains_levels`: "여유", "부족", "고갈" 텍스트 포함 확인 |
| Red | `tests/test_monitor/test_formatter.py` | `test_format_production_queue_returns_str`: 반환 타입 str 확인 |
| Red | `tests/test_monitor/test_formatter.py` | `test_format_main_dashboard_returns_str`: 반환 타입 str 확인 |
| Green | `app/monitor/formatter.py` | `MonitorFormatter` 4개 메서드 구현 (format_order_summary, format_stock_summary, format_production_queue, format_main_dashboard) |
| Refactor | `app/monitor/formatter.py` | 공통 테이블 헤더 로직 분리, 정렬 폭 상수화 |

### Phase 4 – main.py 통합 및 커버리지

| 단계 | 파일 | 작업 내용 |
|------|------|----------|
| Green | `requirements.txt` | pytest, pytest-cov, pytest-mock 의존성 추가 |
| Green | `main.py` | 메뉴 루프 구현: `[1] 주문량 확인 → [2] 재고량 확인 → [0] 종료` |
| 검증 | — | `pytest tests/ -v --cov=app --cov-report=term-missing` 실행 |

---

## 커밋 전략

| prefix | 시점 |
|--------|------|
| `test:` | Red 단계 완료 시 |
| `feat:` | Green 단계 완료 시 |
| `refactor:` | Refactor 단계 완료 시 |

---

## 완료 기준

- [ ] 모든 테스트 통과 (`pytest`)
- [ ] 커버리지 80% 이상
- [ ] Repository는 `MagicMock`으로 격리 (실제 파일 I/O 없음)
- [ ] 모든 formatter 메서드가 `str` 반환 (`print()` 내부 호출 없음)
- [ ] PRD Section 7 검증 기준 테스트 8개 전부 포함
- [ ] REJECTED 주문이 집계에서 제외됨
- [ ] `actual_qty = ceil(shortage / (yield_rate * 0.9))` 계산식 검증 포함
