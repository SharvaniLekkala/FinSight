import pandas as pd
import logging

logger = logging.getLogger(__name__)

def clean_paysim(df: pd.DataFrame) -> pd.DataFrame:
    """Standardize PaySim transaction data.
    - Convert step to datetime (epoch seconds)
    - Ensure amount is numeric
    - Derive date_key (YYYYMMDD) and hour_of_day
    """
    logger.info("Cleaning PaySim dataset")
    df = df.copy()
    # Convert step (seconds since epoch) to datetime
    df["transaction_timestamp"] = pd.to_datetime(df["step"], unit="s")
    df["date_key"] = df["transaction_timestamp"].dt.strftime('%Y%m%d').astype(int)
    df["hour_of_day"] = df["transaction_timestamp"].dt.hour.astype(int)
    # Ensure amount is numeric
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
    # Rename columns for consistency
    rename_map = {
        "nameOrig": "customer_id",
        "nameDest": "merchant_id",
        "oldbalanceOrg": "balance_before",
        "newbalanceOrig": "balance_after",
        "isFraud": "is_fraud",
        "isFlaggedFraud": "is_flagged_fraud",
    }
    df = df.rename(columns=rename_map)
    return df
