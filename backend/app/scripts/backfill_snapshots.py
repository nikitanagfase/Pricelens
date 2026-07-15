"""
scripts/backfill_snapshots.py
─────────────────────────────────────────────
ONE-TIME script — run once to fix old price_snapshots
rows where days_before_travel was saved as NULL
(before the flights.py fix was applied).

Usage:  python -m app.scripts.backfill_snapshots
"""
from datetime import datetime

from app.db.session import SessionLocal
from app.db.models import PriceSnapshot


def backfill():
    db = SessionLocal()
    try:
        rows = (
            db.query(PriceSnapshot)
            .filter(PriceSnapshot.days_before_travel.is_(None))
            .filter(PriceSnapshot.travel_date.isnot(None))
            .all()
        )

        print(f"Found {len(rows)} rows missing days_before_travel...")

        updated = 0
        skipped = 0

        for r in rows:
            try:
                travel_dt = datetime.strptime(r.travel_date, "%Y-%m-%d")
                # use recorded_at as the "search happened on this day" reference
                search_dt = r.recorded_at or datetime.now()
                days_before = (travel_dt - search_dt).days
                r.days_before_travel = max(days_before, 0)
                updated += 1
            except (ValueError, TypeError):
                skipped += 1
                continue

        db.commit()
        print(f"✅ Updated: {updated}")
        print(f"⚠️  Skipped (bad/missing travel_date): {skipped}")

        # sanity check
        final_count = (
            db.query(PriceSnapshot)
            .filter(PriceSnapshot.source == "ignav")
            .filter(PriceSnapshot.days_before_travel.isnot(None))
            .count()
        )
        print(f"Total real+usable snapshots now: {final_count}")

    finally:
        db.close()


if __name__ == "__main__":
    backfill()