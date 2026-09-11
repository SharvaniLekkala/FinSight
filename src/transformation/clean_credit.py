import pandas as pd
import logging

logger = logging.getLogger(__name__)

def clean_credit(df: pd.DataFrame) -> pd.DataFrame:
    """Standardize UCI Credit Card Default dataset.
    - Encode categorical columns (SEX, EDUCATION, MARRIAGE)
    - Derive age_group buckets
    - Ensure numeric columns are proper dtypes
    """
    logger.info("Cleaning Credit dataset")
    df = df.copy()
    # The original Excel sheet has an extra first column (ID) and header row.
    # Assume df already loaded correctly.
    # Encode SEX: 1=male, 2=female
    df["sex"] = df["SEX"].map({1: "male", 2: "female"})
    # Edu: collapse rare categories into "other"
    df["education"] = df["EDUCATION"].replace({0: "other", 5: "other", 6: "other"})
    # Marriage
    df["marriage"] = df["MARRIAGE"].replace({0: "other"})
    # Age group
    bins = [0, 30, 45, 60, 120]
    labels = ["<30", "30-45", "45-60", ">60"]
    df["age_group"] = pd.cut(df["AGE"], bins=bins, labels=labels, right=False)
    # Ensure numeric types for financial columns
    numeric_cols = [col for col in df.columns if "PAY_" in col or "BILL_AMT" in col or "PAY_AMT" in col]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    # Rename ID column for consistency
    df = df.rename(columns={"ID": "customer_id"})
    return df
