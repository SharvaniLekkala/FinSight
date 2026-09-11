import logging
import pathlib
import pandas as pd
import requests
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
import yaml

logger = logging.getLogger(__name__)

def load_db_engine(config_path: str = "config/db.yaml") -> Engine:
    """Load DB connection from YAML and return SQLAlchemy engine."""
    with open(config_path) as f:
        cfg = yaml.safe_load(f)
    conn_str = f"postgresql+psycopg2://{cfg['user']}:{cfg['password']}@{cfg['host']}:{cfg['port']}/{cfg['database']}"
    return create_engine(conn_str)

def download_file(url: str, dest_path: str) -> pathlib.Path:
    """Download a file from URL to dest_path and return the Path."""
    dest = pathlib.Path(dest_path)
    dest.parent.mkdir(parents=True, exist_ok=True)
    logger.info("Downloading %s to %s", url, dest)
    resp = requests.get(url, stream=True, timeout=30)
    resp.raise_for_status()
    with open(dest, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
    return dest

def load_csv_to_stage(table_name: str, csv_path: str, engine: Engine) -> int:
    """Read CSV with pandas and load into staging table. Returns row count."""
    logger.info("Loading %s into staging table %s", csv_path, table_name)
    df = pd.read_csv(csv_path)
    df.to_sql(name=table_name, con=engine, if_exists="replace", index=False, method="multi")
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
    engine.execute(create_sql)
    insert_sql = """
    INSERT INTO ingestion_log (table_name, row_count, status)
    VALUES (%s, %s, %s);
    """
    engine.execute(insert_sql, (table_name, row_count, status))

def ingest_dataset(name: str, url: str, staging_table: str, engine: Engine) -> None:
    """Download, load, and log ingestion for a dataset."""
    try:
        csv_path = download_file(url, f"data/raw/{name}.csv")
        rows = load_csv_to_stage(staging_table, str(csv_path), engine)
        record_ingestion_metadata(engine, staging_table, rows, status="success")
        logger.info("Ingestion of %s completed: %d rows", name, rows)
    except Exception as e:
        logger.exception("Failed ingestion for %s", name)
        record_ingestion_metadata(engine, staging_table, 0, status="failed")
        raise
