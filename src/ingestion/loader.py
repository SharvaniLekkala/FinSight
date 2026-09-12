import logging
import pathlib
import numpy as np
import pandas as pd
import requests
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
import yaml

logger = logging.getLogger(__name__)

def load_db_engine(config_path: str = "config/db.yaml") -> Engine:
    """Load DB connection from YAML and return a SQLAlchemy engine.
    If the target database does not exist, it is created on‑the‑fly
    (using the default "postgres" database as a bootstrap).
    """
    with open(config_path) as f:
        cfg = yaml.safe_load(f)
    # Build connection string for the target DB
    conn_str = f"postgresql+psycopg2://{cfg['user']}:{cfg['password']}@{cfg['host']}:{cfg['port']}/{cfg['database']}"
    try:
        engine = create_engine(conn_str)
        # Test the connection
        with engine.connect() as _:
            pass
        return engine
    except Exception:
        # Database likely does not exist — create it using autocommit
        fallback_conn_str = (
            f"postgresql+psycopg2://{cfg['user']}:{cfg['password']}"
            f"@{cfg['host']}:{cfg['port']}/postgres"
        )
        fallback_engine = create_engine(fallback_conn_str)
        # Use raw DBAPI connection with autocommit so CREATE DATABASE
        # is not wrapped in a transaction block.
        raw_conn = fallback_engine.raw_connection()
        try:
            raw_conn.set_session(autocommit=True)
            cursor = raw_conn.cursor()
            cursor.execute(
                "SELECT 1 FROM pg_database WHERE datname = %s",
                (cfg["database"],),
            )
            if not cursor.fetchone():
                cursor.execute(f'CREATE DATABASE "{cfg["database"]}"')
                logger.info("Created database %s", cfg["database"])
            cursor.close()
        finally:
            raw_conn.close()
        fallback_engine.dispose()
        # Now connect to the newly created target DB
        engine = create_engine(conn_str)
        return engine


def download_file(url: str, dest_path: str) -> pathlib.Path:
    """Download a file from URL to dest_path and return the Path.
    Tries multiple fallback URLs for known datasets.
    Returns None if all download attempts fail.
    """
    dest = pathlib.Path(dest_path)
    dest.parent.mkdir(parents=True, exist_ok=True)

    # Build a list of URLs to try
    urls_to_try = [url]
    if "paysim" in url.lower():
        # The original repo is gone; try common mirrors
        urls_to_try.extend([
            url.replace("master", "main"),
            "https://raw.githubusercontent.com/namebrandon/paysim/main/paysim.csv",
        ])

    for attempt_url in urls_to_try:
        logger.info("Trying to download %s to %s", attempt_url, dest)
        try:
            resp = requests.get(attempt_url, stream=True, timeout=60)
            resp.raise_for_status()
            with open(dest, "wb") as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            logger.info("Download succeeded from %s", attempt_url)
            return dest
        except Exception as e:
            logger.warning("Download failed from %s: %s", attempt_url, e)
            continue

    # All URLs failed
    return None


def generate_paysim_sample(dest_path: str, n_rows: int = 5000) -> pathlib.Path:
    """Generate a realistic synthetic PaySim-style dataset when download fails."""
    logger.info("Generating synthetic PaySim data (%d rows) at %s", n_rows, dest_path)
    dest = pathlib.Path(dest_path)
    dest.parent.mkdir(parents=True, exist_ok=True)

    rng = np.random.default_rng(42)
    types = ["CASH_OUT", "PAYMENT", "CASH_IN", "TRANSFER", "DEBIT"]
    type_probs = [0.35, 0.25, 0.20, 0.15, 0.05]

    df = pd.DataFrame({
        "step": rng.integers(1, 744, size=n_rows),
        "type": rng.choice(types, size=n_rows, p=type_probs),
        "amount": np.round(rng.exponential(scale=50000, size=n_rows), 2),
        "nameOrig": [f"C{rng.integers(100000, 999999)}" for _ in range(n_rows)],
        "oldbalanceOrg": np.round(rng.exponential(scale=100000, size=n_rows), 2),
        "nameDest": [f"M{rng.integers(100000, 999999)}" for _ in range(n_rows)],
        "oldbalanceDest": np.round(rng.exponential(scale=200000, size=n_rows), 2),
        "isFraud": rng.choice([0, 1], size=n_rows, p=[0.98, 0.02]),
        "isFlaggedFraud": 0,
    })
    df["newbalanceOrig"] = np.maximum(0, np.round(df["oldbalanceOrg"] - df["amount"], 2))
    df["newbalanceDest"] = np.round(df["oldbalanceDest"] + df["amount"], 2)
    # Flag a few fraudulent transactions
    fraud_mask = df["isFraud"] == 1
    df.loc[fraud_mask & (df["amount"] > 200000), "isFlaggedFraud"] = 1

    df.to_csv(dest, index=False)
    logger.info("Synthetic PaySim data saved: %d rows", len(df))
    return dest


def generate_credit_sample(dest_path: str, n_rows: int = 3000) -> pathlib.Path:
    """Generate a realistic synthetic UCI Credit Card Default dataset when download fails."""
    logger.info("Generating synthetic credit data (%d rows) at %s", n_rows, dest_path)
    dest = pathlib.Path(dest_path)
    dest.parent.mkdir(parents=True, exist_ok=True)

    rng = np.random.default_rng(123)

    df = pd.DataFrame({
        "ID": range(1, n_rows + 1),
        "LIMIT_BAL": rng.choice([10000, 20000, 30000, 50000, 80000, 100000, 200000, 500000], size=n_rows),
        "SEX": rng.choice([1, 2], size=n_rows),
        "EDUCATION": rng.choice([1, 2, 3, 4], size=n_rows, p=[0.35, 0.40, 0.15, 0.10]),
        "MARRIAGE": rng.choice([1, 2, 3], size=n_rows, p=[0.45, 0.45, 0.10]),
        "AGE": rng.integers(21, 75, size=n_rows),
        "PAY_0": rng.choice([-2, -1, 0, 1, 2, 3, 4], size=n_rows, p=[0.05, 0.10, 0.50, 0.15, 0.10, 0.05, 0.05]),
        "PAY_2": rng.choice([-2, -1, 0, 1, 2, 3], size=n_rows, p=[0.05, 0.10, 0.55, 0.15, 0.10, 0.05]),
        "PAY_3": rng.choice([-2, -1, 0, 1, 2, 3], size=n_rows, p=[0.05, 0.10, 0.55, 0.15, 0.10, 0.05]),
        "PAY_4": rng.choice([-2, -1, 0, 1, 2], size=n_rows, p=[0.05, 0.10, 0.60, 0.15, 0.10]),
        "PAY_5": rng.choice([-2, -1, 0, 1, 2], size=n_rows, p=[0.05, 0.10, 0.60, 0.15, 0.10]),
        "PAY_6": rng.choice([-2, -1, 0, 1, 2], size=n_rows, p=[0.05, 0.10, 0.60, 0.15, 0.10]),
    })
    # Bill and payment amounts
    for i in range(1, 7):
        df[f"BILL_AMT{i}"] = np.round(rng.exponential(scale=20000, size=n_rows), 2)
        df[f"PAY_AMT{i}"] = np.round(rng.exponential(scale=5000, size=n_rows), 2)
    # Default flag
    df["default.payment.next.month"] = rng.choice([0, 1], size=n_rows, p=[0.78, 0.22])

    df.to_csv(dest, index=False)
    logger.info("Synthetic credit data saved: %d rows", len(df))
    return dest


def load_csv_to_stage(table_name: str, csv_path: str, engine: Engine) -> int:
    """Read CSV (or XLS/XLSX) with pandas and load into staging table. Returns row count.
    Detects file format by content magic bytes, not just extension.
    """
    logger.info("Loading %s into staging table %s", csv_path, table_name)
    path = pathlib.Path(csv_path)

    # Detect actual file type by magic bytes
    is_excel = False
    with open(path, "rb") as fh:
        header = fh.read(8)
        # XLS (BIFF) magic: D0 CF 11 E0 A1 B1 1A E1
        # XLSX (ZIP) magic: 50 4B 03 04
        if header[:8] == b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1' or header[:4] == b'PK\x03\x04':
            is_excel = True

    if is_excel:
        logger.info("Detected Excel format for %s", csv_path)
        df = pd.read_excel(csv_path, header=1)  # UCI credit has header on row 2
    else:
        df = pd.read_csv(csv_path)
    with engine.begin() as conn:
        conn.exec_driver_sql(f'DROP TABLE IF EXISTS "{table_name}" CASCADE;')
    df.to_sql(name=table_name, con=engine, if_exists="replace", index=False, method="multi", chunksize=500)
    return len(df)

def record_ingestion_metadata(engine: Engine, table_name: str, row_count: int, status: str = "success") -> None:
    """Insert a simple record into ingestion_log table (creates if missing)."""
    create_sql = """
    CREATE TABLE IF NOT EXISTS ingestion_log (
        id SERIAL PRIMARY KEY,
        table_name TEXT,
        row_count INT,
        status TEXT,
        ingest_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    insert_sql = text("""
    INSERT INTO ingestion_log (table_name, row_count, status)
    VALUES (:table_name, :row_count, :status);
    """)
    with engine.begin() as conn:
        conn.exec_driver_sql(create_sql)
        conn.execute(insert_sql, {"table_name": table_name, "row_count": row_count, "status": status})

def ingest_dataset(name: str, url: str, staging_table: str, engine: Engine) -> None:
    """Download, load, and log ingestion for a dataset.
    If download fails, generates synthetic sample data as fallback.
    """
    try:
        csv_path = download_file(url, f"data/raw/{name}.csv")
        if csv_path is None:
            # Download failed — generate synthetic data
            logger.warning("All download URLs failed for %s. Generating synthetic data.", name)
            if name == "paysim":
                csv_path = generate_paysim_sample(f"data/raw/{name}.csv")
            elif name == "credit":
                csv_path = generate_credit_sample(f"data/raw/{name}.csv")
            else:
                raise RuntimeError(f"No synthetic generator for dataset '{name}'")
        rows = load_csv_to_stage(staging_table, str(csv_path), engine)
        record_ingestion_metadata(engine, staging_table, rows, status="success")
        logger.info("Ingestion of %s completed: %d rows", name, rows)
    except Exception:
        logger.exception("Failed ingestion for %s", name)
        record_ingestion_metadata(engine, staging_table, 0, status="failed")
        raise
