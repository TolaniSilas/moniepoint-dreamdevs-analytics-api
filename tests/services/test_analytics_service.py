"""
unit tests for AnalyticsService (src/services/analytics.py).

each method is tested in isolation by mocking the sqlalchemy session.
no real database connection or running server is required.

run the test with: uv run pytest tests/services/test_analytics_service.py -v
"""

import pytest
from unittest.mock import MagicMock, call, patch
from sqlalchemy.orm import Session
from src.services.analytics import AnalyticsService


def make_row(**kwargs):
    """
    create a lightweight mock row that mimics a sqlalchemy row object.
    the attributes are set from kwargs (e.g. make_row(merchant_id="M1", total=500.0)).
    """
    row = MagicMock()
    for key, value in kwargs.items():
        setattr(row, key, value)
    return row


@pytest.fixture
def db():
    """fresh mock sqlalchemy session for each test."""
    return MagicMock(spec=Session)


@pytest.fixture
def service(db):
    """AnalyticsService instance wired to the mock db."""
    return AnalyticsService(db)



class TestGetTopMerchant:


    def test_returns_merchant_id_and_total_volume(self, service, db):
        """happy path: returns correct merchant_id and rounded total_volume."""

        db.execute.return_value.first.return_value = make_row(
            merchant_id="MRC-001", total=98765.4321
        )
        result = service.get_top_merchant()
        assert result["merchant_id"] == "MRC-001"
        assert result["total_volume"] == 98765.43  # rounded to 2 decimal places (dp)


    def test_total_volume_rounded_to_2dp(self, service, db):
        """total_volume must be rounded to exactly 2 decimal places."""

        db.execute.return_value.first.return_value = make_row(
            merchant_id="MRC-002", total=100.109999
        )
        result = service.get_top_merchant()
        assert result["total_volume"] == 100.11


    def test_no_rows_returns_none_and_zero(self, service, db):
        """when no SUCCESS events exist, merchant_id is None and total_volume is 0.0."""

        db.execute.return_value.first.return_value = None
        result = service.get_top_merchant()
        assert result["merchant_id"] is None
        assert result["total_volume"] == 0.00


    def test_row_with_none_total_returns_zero(self, service, db):
        """if total is None on the row itself, total_volume defaults to 0.0."""

        db.execute.return_value.first.return_value = make_row(
            merchant_id="MRC-003", total=None
        )
        result = service.get_top_merchant()
        assert result["total_volume"] == 0.0


    def test_returns_dict_with_correct_keys(self, service, db):
        """return value must always have merchant_id and total_volume keys."""

        db.execute.return_value.first.return_value = make_row(
            merchant_id="MRC-004", total=500.0
        )
        result = service.get_top_merchant()
        assert set(result.keys()) == {"merchant_id", "total_volume"}


    def test_db_execute_is_called_once(self, service, db):
        """service should only make one DB call for this query."""

        db.execute.return_value.first.return_value = None
        service.get_top_merchant()
        db.execute.assert_called_once()


    def test_large_amount_handled_correctly(self, service, db):
        """very large transaction amounts should not lose precision."""

        db.execute.return_value.first.return_value = make_row(
            merchant_id="MRC-BIG", total=999999999.9899
        )
        result = service.get_top_merchant()
        assert result["total_volume"] == 999999999.99




class TestGetMonthlyActiveMerchants:

    def test_returns_month_to_count_mapping(self, service, db):
        """happy path: returns a dict mapping YYYY-MM strings to integer counts."""

        db.execute.return_value.all.return_value = [
            make_row(month="2024-01", count=10),
            make_row(month="2024-02", count=15),
        ]
        result = service.get_monthly_active_merchants()
        assert result == {"2024-01": 10, "2024-02": 15}


    def test_empty_result_returns_empty_dict(self, service, db):
        """no rows --> empty dict, not an error."""

        db.execute.return_value.all.return_value = []
        result = service.get_monthly_active_merchants()
        assert result == {}


    def test_single_month_returned(self, service, db):
        """works correctly when only one month has data."""

        db.execute.return_value.all.return_value = [
            make_row(month="2024-06", count=7),
        ]
        result = service.get_monthly_active_merchants()
        assert result == {"2024-06": 7}


    def test_month_keys_are_strings(self, service, db):
        """all month keys must be strings (YYYY-MM format)."""

        db.execute.return_value.all.return_value = [
            make_row(month="2024-03", count=5),
        ]
        result = service.get_monthly_active_merchants()
        for key in result.keys():
            assert isinstance(key, str)


    def test_counts_are_integers(self, service, db):
        """all count values must be integers."""

        db.execute.return_value.all.return_value = [
            make_row(month="2024-04", count=20),
            make_row(month="2024-05", count=30),
        ]
        result = service.get_monthly_active_merchants()
        for v in result.values():
            assert isinstance(v, int)


    def test_multiple_months_all_included(self, service, db):
        """all months returned by DB should appear in the result."""

        months = [make_row(month=f"2024-{str(i).zfill(2)}", count=i * 5) for i in range(1, 7)]
        db.execute.return_value.all.return_value = months
        result = service.get_monthly_active_merchants()
        assert len(result) == 6



class TestGetProductAdoption:


    def test_returns_product_to_count_mapping(self, service, db):
        """happy path: returns dict of product --> distinct merchant count."""

        db.execute.return_value.all.return_value = [
            make_row(product="POS", count=500),
            make_row(product="AIRTIME", count=400),
            make_row(product="KYC", count=50),
        ]
        result = service.get_product_adoption()
        assert result["POS"] == 500
        assert result["AIRTIME"] == 400
        assert result["KYC"] == 50


    def test_empty_result_returns_empty_dict(self, service, db):
        """no data --> empty dict."""
        
        db.execute.return_value.all.return_value = []
        result = service.get_product_adoption()
        assert result == {}


    def test_single_product_returned(self, service, db):
        """works correctly when only one product has data."""

        db.execute.return_value.all.return_value = [
            make_row(product="SAVINGS", count=1),
        ]
        result = service.get_product_adoption()
        assert result == {"SAVINGS": 1}


    def test_all_seven_products_returned(self, service, db):
        """all the 7 known products should appear when data exists for all."""

        products = ["POS", "AIRTIME", "BILLS", "CARD_PAYMENT", "SAVINGS", "MONIEBOOK", "KYC"]
        db.execute.return_value.all.return_value = [
            make_row(product=p, count=i * 10) for i, p in enumerate(products, 1)
        ]
        result = service.get_product_adoption()
        assert set(result.keys()) == set(products)


    def test_product_with_single_merchant(self, service, db):
        """a product used by only 1 merchant should still be included."""

        db.execute.return_value.all.return_value = [
            make_row(product="MONIEBOOK", count=1),
        ]
        result = service.get_product_adoption()
        assert result["MONIEBOOK"] == 1


    def test_counts_are_integers(self, service, db):
        """all count values must be integers."""

        db.execute.return_value.all.return_value = [
            make_row(product="BILLS", count=99),
        ]
        result = service.get_product_adoption()
        for v in result.values():
            assert isinstance(v, int)




class TestGetKycFunnel:


    def test_returns_all_three_stages(self, service, db):
        """happy path: ensure all the 3 KYC stages are present with correct counts."""

        db.execute.return_value.scalar.side_effect = [100, 75, 40]
        result = service.get_kyc_funnel()
        assert result["documents_submitted"] == 100
        assert result["verifications_completed"] == 75
        assert result["tier_upgrades"] == 40


    def test_no_kyc_data_returns_zeros(self, service, db):
        """when scalar returns None (no rows), all counts default to 0."""

        db.execute.return_value.scalar.return_value = None
        result = service.get_kyc_funnel()
        assert result["documents_submitted"] == 0
        assert result["verifications_completed"] == 0
        assert result["tier_upgrades"] == 0


    def test_funnel_shape_decreases(self, service, db):
        """submitted >= completed >= upgraded is the expected funnel shape."""

        db.execute.return_value.scalar.side_effect = [200, 150, 80]
        result = service.get_kyc_funnel()
        assert result["documents_submitted"] >= result["verifications_completed"]
        assert result["verifications_completed"] >= result["tier_upgrades"]


    def test_returns_dict_with_correct_keys(self, service, db):
        """return value must contain exactly the three expected keys."""

        db.execute.return_value.scalar.side_effect = [10, 8, 5]
        result = service.get_kyc_funnel()
        assert set(result.keys()) == {
            "documents_submitted",
            "verifications_completed",
            "tier_upgrades",
        }


    def test_db_called_three_times(self, service, db):
        """each KYC stage requires one separate DB call — total of 3."""

        db.execute.return_value.scalar.side_effect = [50, 30, 10]
        service.get_kyc_funnel()
        assert db.execute.call_count == 3


    def test_all_counts_are_integers(self, service, db):
        """all returned counts must be integers."""

        db.execute.return_value.scalar.side_effect = [10, 8, 3]
        result = service.get_kyc_funnel()
        for v in result.values():
            assert isinstance(v, int)


    def test_partial_funnel_data(self, service, db):
        """only some stages have data — others should default to 0."""

        db.execute.return_value.scalar.side_effect = [50, 0, None]
        result = service.get_kyc_funnel()
        assert result["documents_submitted"] == 50
        assert result["verifications_completed"] == 0
        assert result["tier_upgrades"] == 0




class TestGetFailureRates:


    def test_returns_list_of_dicts(self, service, db):
        """happy path: returns a list of {product, failure_rate} dicts."""

        db.execute.return_value.all.return_value = [
            make_row(product="POS", failure_rate=12.567),
            make_row(product="AIRTIME", failure_rate=5.0),
        ]
        result = service.get_failure_rates()
        assert isinstance(result, list)
        assert result[0]["product"] == "POS"
        assert result[0]["failure_rate"] == 12.6  # rounded to 1 decimal place (dp).


    def test_failure_rate_rounded_to_1dp(self, service, db):
        """failure rates must be rounded to 1 decimal place."""

        db.execute.return_value.all.return_value = [
            make_row(product="BILLS", failure_rate=33.349),
        ]
        result = service.get_failure_rates()
        assert result[0]["failure_rate"] == 33.3


    def test_zero_failures_returns_0_rate(self, service, db):
        """a product with no FAILED events should have failure_rate of 0.0."""

        db.execute.return_value.all.return_value = [
            make_row(product="SAVINGS", failure_rate=0.0),
        ]
        result = service.get_failure_rates()
        assert result[0]["failure_rate"] == 0.0


    def test_all_failed_returns_100_rate(self, service, db):
        """a product with only FAILED events should have failure_rate of 100.0."""

        db.execute.return_value.all.return_value = [
            make_row(product="MONIEBOOK", failure_rate=100.0),
        ]
        result = service.get_failure_rates()
        assert result[0]["failure_rate"] == 100.0


    def test_none_failure_rate_defaults_to_zero(self, service, db):
        """if failure_rate is None (nullif triggered), it defaults to 0.0."""

        db.execute.return_value.all.return_value = [
            make_row(product="KYC", failure_rate=None),
        ]
        result = service.get_failure_rates()
        assert result[0]["failure_rate"] == 0.0


    def test_empty_result_returns_empty_list(self, service, db):
        """no data --> empty list, not an error."""

        db.execute.return_value.all.return_value = []
        result = service.get_failure_rates()
        assert result == []


    def test_each_item_has_required_keys(self, service, db):
        """every item in the result list must have product and failure_rate keys."""

        db.execute.return_value.all.return_value = [
            make_row(product="CARD_PAYMENT", failure_rate=7.8),
        ]
        result = service.get_failure_rates()
        for item in result:
            assert "product" in item
            assert "failure_rate" in item


    def test_sorted_descending_by_failure_rate(self, service, db):
        """results must be ordered highest failure rate first."""

        db.execute.return_value.all.return_value = [
            make_row(product="KYC", failure_rate=50.0),
            make_row(product="POS", failure_rate=20.0),
            make_row(product="AIRTIME", failure_rate=5.0),
        ]
        result = service.get_failure_rates()
        rates = [item["failure_rate"] for item in result]
        assert rates == sorted(rates, reverse=True)


    def test_multiple_products_all_included(self, service, db):
        """all products returned by DB should appear in result."""

        db.execute.return_value.all.return_value = [
            make_row(product=p, failure_rate=float(i))
            for i, p in enumerate(["POS", "AIRTIME", "BILLS", "KYC"], 1)
        ]
        result = service.get_failure_rates()
        assert len(result) == 4