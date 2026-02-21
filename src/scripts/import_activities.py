"""
import CSV activity files into PostgreSQL.
handles malformed rows by skipping them and continuing.
run from project root: python -m src.scripts.import_activities
"""
import csv
import re
import sys
from decimal import Decimal, InvalidOperation
from pathlib import Path
from uuid import UUID
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session
from src.core.config import settings
from src.db.base import Base, SessionLocal, engine
from src.models import Activity

# extract the pattern to match files like activities_20240101.csv, activities_20240102.csv and so on.
CSV_PATTERN = re.compile(r"activities_(\d{8})\.csv")


def parse_timestamp(value: str) -> str | None:
    if not value or not value.strip():
        return None
    return value.strip()


def parse_amount(value: str) -> Decimal | None:
    if value is None or (isinstance(value, str) and not value.strip()):
        return Decimal("0")
    
    try:
        return Decimal(str(value).strip()).quantize(Decimal("0.01"))
    
    except (InvalidOperation, ValueError):
        return None


def parse_uuid(value: str) -> UUID | None:
    if not value or not str(value).strip():
        return None
    try:
        return UUID(str(value).strip())
    except (ValueError, TypeError):
        return None


def row_to_activity(row: dict) -> dict | None:

    event_id = parse_uuid(row.get("event_id", ""))
    if event_id is None:
        return None
    
    merchant_id = (row.get("merchant_id") or "").strip()
    if not merchant_id:
        return None
    
    product = (row.get("product") or "").strip()
    if not product:
        return None
    
    event_type = (row.get("event_type") or "").strip()
    if not event_type:
        return None
    
    status = (row.get("status") or "").strip()
    if not status:
        return None
    
    amount = parse_amount(row.get("amount", "0"))
    if amount is None:
        return None

    ts_raw = parse_timestamp(row.get("event_timestamp", ""))
    event_timestamp = None
    if ts_raw:
        try:
            from datetime import datetime
            event_timestamp = datetime.fromisoformat(ts_raw.replace("Z", "+00:00"))
        except Exception:
            pass

    return {
        "event_id": event_id,
        "merchant_id": merchant_id,
        "event_timestamp": event_timestamp,
        "product": product,
        "event_type": event_type,
        "amount": amount,
        "status": status,
        "channel": (row.get("channel") or "").strip() or None,
        "region": (row.get("region") or "").strip() or None,
        "merchant_tier": (row.get("merchant_tier") or "").strip() or None,
    }


def import_csv_file(path: Path, db: Session) -> tuple[int, int]:
    """import one CSV. uses ON CONFLICT DO NOTHING so re-runs skip existing event_ids."""
    processed = 0
    skipped = 0
    batch = []
    batch_size = 5000

    with open(path, newline="", encoding="utf-8", errors="replace") as file_object:
        reader = csv.DictReader(file_object)

        if reader.fieldnames is None:
            return 0, 0
        for row in reader:
            record = row_to_activity(row)
            if record is None:
                skipped += 1
                continue
            batch.append(record)

            if len(batch) >= batch_size:
                stmt = pg_insert(Activity).values(batch).on_conflict_do_nothing(
                    index_elements=["event_id"]
                )
                db.execute(stmt)
                db.commit()
                processed += len(batch)
                batch = []
        if batch:
            stmt = pg_insert(Activity).values(batch).on_conflict_do_nothing(
                index_elements=["event_id"]
            )
            db.execute(stmt)
            db.commit()
            processed += len(batch)
    return processed, skipped


def run_import(data_dir: Path | None = None) -> None:

    data_dir = data_dir or settings.data_dir
    if not data_dir.is_dir():
        print(f"Data directory not found: {data_dir}", file=sys.stderr)
        sys.exit(1)

    Base.metadata.create_all(bind=engine)
    csv_files = sorted(
        p for p in data_dir.iterdir()
        if p.is_file() and CSV_PATTERN.match(p.name)
    )
    if not csv_files:
        print(f"No activities_YYYYMMDD.csv files in {data_dir}", file=sys.stderr)
        sys.exit(1)

    total_processed = 0
    total_skipped = 0
    db = SessionLocal()

    try:
        for path in csv_files:
            processed, skipped = import_csv_file(path, db)
            total_processed += processed
            total_skipped += skipped
            print(f"  {path.name}: {processed} rows processed, {skipped} skipped (malformed)")
        print(f"Done. Total processed: {total_processed}, total skipped (malformed): {total_skipped}")

    finally:
        db.close()


if __name__ == "__main__":
    run_import()
