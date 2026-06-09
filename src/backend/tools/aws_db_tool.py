"""
AWS RDS (PostgreSQL) persistence tool.

During the build phase this connects to the local PostgreSQL container defined
in docker-compose (set DATABASE_URL). In production the same code points at
Amazon RDS. If the database is unreachable the functions return a status flag
instead of raising, so the agent graph keeps running and reports degraded
persistence rather than crashing.
"""
import os


def _engine():
    url = os.getenv("DATABASE_URL")
    if not url:
        return None
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+psycopg://")
    elif url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+psycopg://")
    url = url.replace("@db:", "@localhost:")
    try:
        from sqlalchemy import create_engine

        return create_engine(url, pool_pre_ping=True, connect_args={'connect_timeout': 3})
    except Exception:  # noqa: BLE001
        return None


def store_user_result(record: dict) -> dict:
    """
    Persist an anonymised user test result. Returns {"persisted": bool, "note": str}.
    The table is created on first use to keep the build phase self-contained.
    """
    engine = _engine()
    if engine is None:
        return {"persisted": False, "note": "DATABASE_URL not set or driver unavailable."}

    try:
        from sqlalchemy import text

        with engine.begin() as conn:
            conn.execute(
                text(
                    """
                    CREATE TABLE IF NOT EXISTS user_test_result (
                        id SERIAL PRIMARY KEY,
                        anonymised_user_id TEXT,
                        area TEXT,
                        overall_risk TEXT,
                        failed_parameters TEXT,
                        recommended_action TEXT,
                        created_at TIMESTAMPTZ DEFAULT now()
                    )
                    """
                )
            )
            conn.execute(
                text(
                    """
                    INSERT INTO user_test_result
                        (anonymised_user_id, area, overall_risk, failed_parameters, recommended_action)
                    VALUES (:uid, :area, :risk, :failed, :action)
                    """
                ),
                {
                    "uid": record.get("anonymised_user_id", ""),
                    "area": record.get("area"),
                    "risk": record.get("overall_risk", ""),
                    "failed": ", ".join(record.get("failed_parameters", [])),
                    "action": record.get("recommended_action", ""),
                },
            )
        return {"persisted": True, "note": ""}
    except Exception as exc:  # noqa: BLE001
        return {"persisted": False, "note": f"DB write failed: {exc}"}
