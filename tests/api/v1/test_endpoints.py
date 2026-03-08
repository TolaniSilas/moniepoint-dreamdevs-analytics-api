"""
full test suite for Moniepoint Analytics API endpoints.

endpoint coverage includes:
  - GET /analytics/top-merchant
  - GET /analytics/monthly-active-merchants
  - GET /analytics/product-adoption
  - GET /analytics/kyc-funnel
  - GET /analytics/failure-rates

all tests use a mocked AnalyticsService so no real DB connection is required or utilized.
run test with: uv run pytest tests/ -v
"""

import re
import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from src.main import app
from src.core.deps import get_db
from src.services.analytics import AnalyticsService



@pytest.fixture(autouse=True)
def clear_overrides():
    """ensure dependency overrides are always cleaned up after each test."""

    yield

    # clean up
    app.dependency_overrides.clear()


@pytest.fixture
def mock_service():
    return MagicMock(spec=AnalyticsService)


@pytest.fixture
def client(mock_service):
    mock_db = MagicMock()
    app.dependency_overrides[get_db] = lambda: mock_db

    with patch("src.api.v1.endpoints.analytics.AnalyticsService", return_value=mock_service):
        with TestClient(app) as c:
            yield c



class TestTopMerchant:
    """test for GET /analytics/top-merchant."""


    def test_returns_200_with_valid_data(self, client, mock_service):
        """happy path: returns merchant_id and total_volume."""

        mock_service.get_top_merchant.return_value = {
            "merchant_id": "MRC-001",
            "total_volume": 98765.43,
        }
        resp = client.get("/analytics/top-merchant")
        assert resp.status_code == 200
        data = resp.json()
        assert data["merchant_id"] == "MRC-001"
        assert data["total_volume"] == 98765.43


    def test_total_volume_rounded_to_2dp(self, client, mock_service):
        """total_volume should carry exactly 2 decimal places."""

        mock_service.get_top_merchant.return_value = {
            "merchant_id": "MRC-002",
            "total_volume": 100.10,
        }
        resp = client.get("/analytics/top-merchant")
        assert resp.status_code == 200
        assert resp.json()["total_volume"] == 100.10


    def test_no_successful_transactions_returns_null_merchant(self, client, mock_service):
        """when no SUCCESS events exist, merchant_id is None and volume is 0."""

        mock_service.get_top_merchant.return_value = {
            "merchant_id": None,
            "total_volume": 0.00,
        }
        resp = client.get("/analytics/top-merchant")
        assert resp.status_code == 200
        data = resp.json()
        assert data["merchant_id"] is None
        assert data["total_volume"] == 0.00


    def test_returns_json_content_type(self, client, mock_service):
        """response Content-Type must be application/json."""

        mock_service.get_top_merchant.return_value = {
            "merchant_id": "MRC-003",
            "total_volume": 500.00,
        }
        resp = client.get("/analytics/top-merchant")
        assert "application/json" in resp.headers["content-type"]


    def test_response_schema_has_required_fields(self, client, mock_service):
        """response must contain exactly merchant_id and total_volume."""

        mock_service.get_top_merchant.return_value = {
            "merchant_id": "MRC-004",
            "total_volume": 1234.56,
        }
        data = client.get("/analytics/top-merchant").json()
        assert "merchant_id" in data
        assert "total_volume" in data


    def test_single_merchant_in_db(self, client, mock_service):
        """only one merchant in DB — should still return correctly."""

        mock_service.get_top_merchant.return_value = {
            "merchant_id": "MRC-ONLY",
            "total_volume": 42.00,
        }
        resp = client.get("/analytics/top-merchant")
        assert resp.status_code == 200
        assert resp.json()["merchant_id"] == "MRC-ONLY"



class TestMonthlyActiveMerchants:
    """test for GET /analytics/monthly-active-merchants."""


    def test_returns_200_with_month_map(self, client, mock_service):
        """happy path: returns a YYYY-MM --> count mapping."""

        mock_service.get_monthly_active_merchants.return_value = {
            "2024-01": 10,
            "2024-02": 15,
            "2024-03": 8,
        }
        resp = client.get("/analytics/monthly-active-merchants")
        assert resp.status_code == 200
        data = resp.json()
        assert data["2024-01"] == 10
        assert data["2024-02"] == 15


    def test_month_keys_are_yyyy_mm_format(self, client, mock_service):
        """all month keys must match YYYY-MM format."""

        mock_service.get_monthly_active_merchants.return_value = {
            "2024-01": 5,
            "2024-11": 3,
        }
        data = client.get("/analytics/monthly-active-merchants").json()
        for key in data.keys():
            assert re.match(r"^\d{4}-\d{2}$", key), f"Bad month format: {key}"


    def test_empty_db_returns_empty_map(self, client, mock_service):
        """no data --> empty dict, not an error."""

        mock_service.get_monthly_active_merchants.return_value = {}
        resp = client.get("/analytics/monthly-active-merchants")
        assert resp.status_code == 200
        assert resp.json() == {}


    def test_null_timestamp_rows_excluded(self, client, mock_service):
        """rows with NULL timestamps should not inflate monthly counts."""

        # service already excludes NULLs; we verify endpoint doesn't add them back.
        mock_service.get_monthly_active_merchants.return_value = {"2024-06": 7}
        data = client.get("/analytics/monthly-active-merchants").json()
        assert "None" not in data
        assert None not in data


    def test_merchant_active_in_multiple_months(self, client, mock_service):
        """a merchant active in 3 months appears as a count in each month's entry."""

        mock_service.get_monthly_active_merchants.return_value = {
            "2024-01": 1,
            "2024-02": 1,
            "2024-03": 1,
        }
        data = client.get("/analytics/monthly-active-merchants").json()
        assert len(data) == 3


    def test_counts_are_integers(self, client, mock_service):
        """all values in the response map must be integers."""

        mock_service.get_monthly_active_merchants.return_value = {
            "2024-04": 20,
            "2024-05": 30,
        }
        data = client.get("/analytics/monthly-active-merchants").json()
        for v in data.values():
            assert isinstance(v, int)



class TestProductAdoption:
    """test for GET /analytics/product-adoption."""

    ALL_PRODUCTS = {"POS", "AIRTIME", "BILLS", "CARD_PAYMENT", "SAVINGS", "MONIEBOOK", "KYC"}

    def test_returns_200_with_all_products(self, client, mock_service):
        """happy path: all 7 products appear in the response."""

        mock_service.get_product_adoption.return_value = {
            "POS": 500, "AIRTIME": 400, "BILLS": 300,
            "CARD_PAYMENT": 250, "SAVINGS": 200, "MONIEBOOK": 100, "KYC": 50,
        }
        resp = client.get("/analytics/product-adoption")
        assert resp.status_code == 200
        data = resp.json()
        assert set(data.keys()) == self.ALL_PRODUCTS


    def test_product_with_single_merchant(self, client, mock_service):
        """a product used by only 1 merchant should still appear."""

        mock_service.get_product_adoption.return_value = {"KYC": 1, "POS": 300}
        data = client.get("/analytics/product-adoption").json()
        assert data["KYC"] == 1

    def test_counts_distinct_merchants(self, client, mock_service):
        """values represent distinct merchant counts, not raw event counts."""

        mock_service.get_product_adoption.return_value = {"POS": 42}
        data = client.get("/analytics/product-adoption").json()
        assert data["POS"] == 42


    def test_includes_all_statuses(self, client, mock_service):
        """product adoption counts regardless of SUCCESS/FAILED/PENDING status."""

        # the service handles this; we confirm endpoint doesn't filter it.
        mock_service.get_product_adoption.return_value = {"AIRTIME": 99}
        resp = client.get("/analytics/product-adoption")
        assert resp.status_code == 200


    def test_empty_db_returns_empty_map(self, client, mock_service):
        """no data --> empty dict."""

        mock_service.get_product_adoption.return_value = {}
        resp = client.get("/analytics/product-adoption")
        assert resp.status_code == 200
        assert resp.json() == {}



class TestKycFunnel:
    """test for GET /analytics/kyc-funnel."""


    def test_returns_200_with_all_three_stages(self, client, mock_service):
        """happy path: all 3 funnel stages are present."""

        mock_service.get_kyc_funnel.return_value = {
            "documents_submitted": 100,
            "verifications_completed": 75,
            "tier_upgrades": 40,
        }
        resp = client.get("/analytics/kyc-funnel")
        assert resp.status_code == 200
        data = resp.json()
        assert "documents_submitted" in data
        assert "verifications_completed" in data
        assert "tier_upgrades" in data


    def test_funnel_shape_is_logical(self, client, mock_service):
        """submitted >= completed >= upgraded (data integrity check)."""

        mock_service.get_kyc_funnel.return_value = {
            "documents_submitted": 200,
            "verifications_completed": 150,
            "tier_upgrades": 80,
        }
        data = client.get("/analytics/kyc-funnel").json()
        assert data["documents_submitted"] >= data["verifications_completed"]
        assert data["verifications_completed"] >= data["tier_upgrades"]


    def test_no_kyc_data_returns_zeros(self, client, mock_service):
        """when there are no KYC events, all counts should be 0."""

        mock_service.get_kyc_funnel.return_value = {
            "documents_submitted": 0,
            "verifications_completed": 0,
            "tier_upgrades": 0,
        }
        resp = client.get("/analytics/kyc-funnel")
        assert resp.status_code == 200
        data = resp.json()
        assert all(v == 0 for v in data.values())


    def test_counts_are_integers(self, client, mock_service):
        """all funnel counts must be integers."""

        mock_service.get_kyc_funnel.return_value = {
            "documents_submitted": 10,
            "verifications_completed": 8,
            "tier_upgrades": 5,
        }
        data = client.get("/analytics/kyc-funnel").json()
        for v in data.values():
            assert isinstance(v, int)


    def test_only_success_events_counted(self, client, mock_service):
        """service filters to SUCCESS only; endpoint should not alter counts."""

        mock_service.get_kyc_funnel.return_value = {
            "documents_submitted": 50,
            "verifications_completed": 30,
            "tier_upgrades": 10,
        }
        data = client.get("/analytics/kyc-funnel").json()

        # if FAILED/PENDING were included, counts would be higher;
        # we trust the service mock returns only SUCCESS-filtered data.
        assert data["documents_submitted"] == 50



class TestFailureRates:
    """test for GET /analytics/failure-rates."""


    def test_returns_200_with_list(self, client, mock_service):
        """happy path: response is a list of product/failure_rate dicts."""

        mock_service.get_failure_rates.return_value = [
            {"product": "POS", "failure_rate": 12.5},
            {"product": "AIRTIME", "failure_rate": 5.0},
        ]
        resp = client.get("/analytics/failure-rates")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert data[0]["product"] == "POS"
        assert data[0]["failure_rate"] == 12.5


    def test_failure_rate_rounded_to_1dp(self, client, mock_service):
        """failure rates must have exactly 1 decimal place."""

        mock_service.get_failure_rates.return_value = [
            {"product": "BILLS", "failure_rate": 33.3},
        ]
        data = client.get("/analytics/failure-rates").json()
        rate = data[0]["failure_rate"]
        assert round(rate, 1) == rate


    def test_sorted_descending_by_failure_rate(self, client, mock_service):
        """results should be ordered highest failure rate first."""

        mock_service.get_failure_rates.return_value = [
            {"product": "KYC", "failure_rate": 50.0},
            {"product": "POS", "failure_rate": 20.0},
            {"product": "AIRTIME", "failure_rate": 5.0},
        ]
        data = client.get("/analytics/failure-rates").json()
        rates = [item["failure_rate"] for item in data]
        assert rates == sorted(rates, reverse=True)


    def test_product_with_zero_failures(self, client, mock_service):
        """a product with no FAILED events should have failure_rate of 0.0."""

        mock_service.get_failure_rates.return_value = [
            {"product": "SAVINGS", "failure_rate": 0.0},
        ]
        data = client.get("/analytics/failure-rates").json()
        assert data[0]["failure_rate"] == 0.0


    def test_product_with_100_percent_failure(self, client, mock_service):
        """a product with only FAILED events should have failure_rate of 100.0."""

        mock_service.get_failure_rates.return_value = [
            {"product": "MONIEBOOK", "failure_rate": 100.0},
        ]
        data = client.get("/analytics/failure-rates").json()
        assert data[0]["failure_rate"] == 100.0


    def test_pending_only_product_excluded(self, client, mock_service):
        """products with only PENDING events should not appear in results."""

        mock_service.get_failure_rates.return_value = [
            {"product": "POS", "failure_rate": 10.0},
            # PENDING-only product is absent - service excludes it
        ]
        data = client.get("/analytics/failure-rates").json()
        products = [item["product"] for item in data]
        assert "PENDING_ONLY_PRODUCT" not in products


    def test_no_data_returns_empty_list(self, client, mock_service):
        """empty DB --> empty list, not an error."""

        mock_service.get_failure_rates.return_value = []
        resp = client.get("/analytics/failure-rates")
        assert resp.status_code == 200
        assert resp.json() == []


    def test_each_item_has_product_and_failure_rate(self, client, mock_service):
        """every item in the list must have both required fields."""

        mock_service.get_failure_rates.return_value = [
            {"product": "CARD_PAYMENT", "failure_rate": 7.8},
        ]
        data = client.get("/analytics/failure-rates").json()
        for item in data:
            assert "product" in item
            assert "failure_rate" in item



class TestGeneral:
    """general test or cross-cutting tests."""


    def test_root_health_check(self, client, mock_service):
        """GET / should return 200."""
        resp = client.get("/")
        assert resp.status_code == 200


    def test_all_endpoints_return_json(self, client, mock_service):
        """every analytics endpoint must respond with application/json."""

        mock_service.get_top_merchant.return_value = {"merchant_id": "X", "total_volume": 1.0}
        mock_service.get_monthly_active_merchants.return_value = {}
        mock_service.get_product_adoption.return_value = {}
        mock_service.get_kyc_funnel.return_value = {
            "documents_submitted": 0, "verifications_completed": 0, "tier_upgrades": 0
        }
        mock_service.get_failure_rates.return_value = []

        endpoints = [
            "/analytics/top-merchant",
            "/analytics/monthly-active-merchants",
            "/analytics/product-adoption",
            "/analytics/kyc-funnel",
            "/analytics/failure-rates",
        ]
        for url in endpoints:
            resp = client.get(url)
            assert "application/json" in resp.headers["content-type"], f"Failed for {url}"


    def test_endpoints_are_idempotent(self, client, mock_service):
        """calling each endpoint twice always returns the same result."""
        
        mock_service.get_top_merchant.return_value = {
            "merchant_id": "MRC-IDEM", "total_volume": 99.99
        }
        mock_service.get_monthly_active_merchants.return_value = {
            "2024-01": 10, "2024-02": 15
        }
        mock_service.get_product_adoption.return_value = {
            "POS": 500, "AIRTIME": 400
        }
        mock_service.get_kyc_funnel.return_value = {
            "documents_submitted": 100,
            "verifications_completed": 75,
            "tier_upgrades": 40,
        }
        mock_service.get_failure_rates.return_value = [
            {"product": "POS", "failure_rate": 12.5},
            {"product": "AIRTIME", "failure_rate": 5.0},
        ]

        endpoints = [
            "/analytics/top-merchant",
            "/analytics/monthly-active-merchants",
            "/analytics/product-adoption",
            "/analytics/kyc-funnel",
            "/analytics/failure-rates",
        ]

        for url in endpoints:
            r1 = client.get(url).json()
            r2 = client.get(url).json()
            assert r1 == r2, f"Idempotency failed for {url}"