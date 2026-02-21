"""business logic for moniepoint analytics services: the queries and aggregations."""
from sqlalchemy import case, func, select, and_
from sqlalchemy.orm import Session

from src.models import Activity


class AnalyticsService:
    """Service for analytics queries over merchant activity data."""

    def __init__(self, db: Session) -> None:

        # initialize the db session.
        self._db = db


    def get_top_merchant(self) -> dict:
        """method for merchant with highest total successful transaction amount across all products."""

        # subquery to calculate total successful volume per merchant (to return merchant with highest total volume).
        subq = (
            select(Activity.merchant_id, func.sum(Activity.amount).label("total"))
            .where(Activity.status == "SUCCESS")
            .group_by(Activity.merchant_id)
            .order_by(func.sum(Activity.amount).desc())
            .limit(1)
        )

        # execute the subquery and fetch the top row.
        row = self._db.execute(subq).first()

        # if no successful transactions found, return None for merchant_id and 0 for the total volume.
        if not row:
            return {"merchant_id": None, "total_volume": 0.00}
        
        # convert total to float and round to 2 decimal places for proper response formatting.
        total = float(row.total) if row.total is not None else 0.0

        return {"merchant_id": row.merchant_id, "total_volume": round(total, 2)}


    def get_monthly_active_merchants(self) -> dict[str, int]:
        """method for unique merchants with at least one successful event per month."""

        # use date_trunc to group by month (truncated-timestamp) and extract month in YYYY-MM format.
        month = func.date_trunc("month", Activity.event_timestamp)

        # query to count unique merchants per month (with at least a succssful event) and sort by month.
        stmt = (
            select(
                func.to_char(month, "YYYY-MM").label("month"),
                func.count(func.distinct(Activity.merchant_id)).label("count"),
            )
            .where(
                and_(
                    Activity.status == "SUCCESS",
                    Activity.event_timestamp.isnot(None),
                )
            )
            .group_by(month)
            .order_by(month)
        )

        # execute the query.
        rows = self._db.execute(stmt).all()

        return {row.month: row.count for row in rows}


    def get_product_adoption(self) -> dict[str, int]:
        """method for unique merchant count per product, sorted by count descending."""

        # query to count unique merchants per products and sort in a descending order.
        stmt = (
            select(
                Activity.product,
                func.count(func.distinct(Activity.merchant_id)).label("count"),
            )
            .group_by(Activity.product)
            .order_by(func.count(func.distinct(Activity.merchant_id)).desc())
        )

        # execute the query.
        rows = self._db.execute(stmt).all()

        return {row.product: row.count for row in rows}


    def get_kyc_funnel(self) -> dict[str, int]:
        """method for KYC conversion funnel: unique merchants at each stage (successful events only)."""

        # condition to filter only successful KYC events.
        kyc_success = and_(Activity.product == "KYC", Activity.status == "SUCCESS")

        # count unique merchants at each KYC stage using condition aggregations.
        docs = self._db.execute(
            select(func.count(func.distinct(Activity.merchant_id))).where(
                and_(kyc_success, Activity.event_type == "DOCUMENT_SUBMITTED")
            )
        ).scalar() or 0

        verif = self._db.execute(
            select(func.count(func.distinct(Activity.merchant_id))).where(
                and_(kyc_success, Activity.event_type == "VERIFICATION_COMPLETED")
            )
        ).scalar() or 0

        tier = self._db.execute(
            select(func.count(func.distinct(Activity.merchant_id))).where(
                and_(kyc_success, Activity.event_type == "TIER_UPGRADE")
            )
        ).scalar() or 0

        return {
            "documents_submitted": docs,
            "verifications_completed": verif,
            "tier_upgrades": tier,
        }


    def get_failure_rates(self) -> list[dict]:
        """method for failure rate per product: (FAILED / (SUCCESS + FAILED)) * 100; exclude PENDING; sort descending."""

        # use conditional aggregation to count failed transactions.
        failed = func.sum(case((Activity.status == "FAILED", 1), else_=0))

        # use conditional aggregation to count successful transactions.
        success = func.sum(case((Activity.status == "SUCCESS", 1), else_=0))

        # 
        total_resolved = failed + success

        # calculate failure rate and handle division by zero error with nullif.
        rate_expr = (100.0 * failed / func.nullif(total_resolved, 0)).label("failure_rate")

        # query products with their failure rates (excluding PENDING scenarios).
        stmt = (
            select(Activity.product, rate_expr)
            .where(Activity.status.in_(["SUCCESS", "FAILED"]))
            .group_by(Activity.product)
            .order_by(rate_expr.desc())
        )

        # execute the query and format results.
        rows = self._db.execute(stmt).all()

        return [
            {"product": row.product, "failure_rate": round(float(row.failure_rate or 0), 1)}
            for row in rows
        ]
