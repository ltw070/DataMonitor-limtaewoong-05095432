"""Phase 1 - Red: Sample 도메인 모델 테스트"""
import pytest
from app.model.sample import Sample


class TestSample:
    def test_create_sample_with_all_fields(self):
        sample = Sample(
            sample_id="S001",
            name="실리콘 웨이퍼-8인치",
            stock=500,
            yield_rate=0.95,
            avg_production_time=120.0,
        )
        assert sample.sample_id == "S001"
        assert sample.name == "실리콘 웨이퍼-8인치"
        assert sample.stock == 500
        assert sample.yield_rate == 0.95
        assert sample.avg_production_time == 120.0

    def test_sample_id_is_str(self):
        sample = Sample(
            sample_id="S002",
            name="SiC 파워기판-6인치",
            stock=100,
            yield_rate=0.80,
            avg_production_time=90.0,
        )
        assert isinstance(sample.sample_id, str)

    def test_sample_stock_is_int(self):
        sample = Sample(
            sample_id="S003",
            name="산화막 웨이퍼-SiO2",
            stock=0,
            yield_rate=0.75,
            avg_production_time=60.0,
        )
        assert isinstance(sample.stock, int)
        assert sample.stock == 0

    def test_sample_yield_rate_is_float(self):
        sample = Sample(
            sample_id="S004",
            name="GaN 에피 기판-4인치",
            stock=200,
            yield_rate=0.88,
            avg_production_time=150.0,
        )
        assert isinstance(sample.yield_rate, float)

    def test_sample_avg_production_time_is_float(self):
        sample = Sample(
            sample_id="S005",
            name="InP 기판-2인치",
            stock=50,
            yield_rate=0.70,
            avg_production_time=200.0,
        )
        assert isinstance(sample.avg_production_time, float)
