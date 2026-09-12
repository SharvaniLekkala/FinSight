"""Data-quality validation rules for FinSight staging tables.

Each rule function receives a DataFrame (and optional parameters) and returns
a ValidationResult named-tuple with:
    rule_name   – human-readable rule identifier
    passed      – True if the check passes (no issues found)
    issue_count – number of rows / items that failed the check
"""
import logging
from typing import List, NamedTuple

import pandas as pd

logger = logging.getLogger(__name__)


class ValidationResult(NamedTuple):
    rule_name: str
    passed: bool
    issue_count: int


# ---------------------------------------------------------------------------
# Rule implementations
# ---------------------------------------------------------------------------

def check_missing_values(df: pd.DataFrame, required_columns: List[str]) -> ValidationResult:
    """Check for missing (null / NaN) values in the required columns."""
    rule_name = "missing_values"
    # Count rows that have at least one null in the required columns
    present_cols = [c for c in required_columns if c in df.columns]
    missing_mask = df[present_cols].isnull().any(axis=1)
    issue_count = int(missing_mask.sum())
    passed = issue_count == 0
    logger.info("Rule %s: passed=%s, issues=%d", rule_name, passed, issue_count)
    return ValidationResult(rule_name=rule_name, passed=passed, issue_count=issue_count)


def check_duplicates(df: pd.DataFrame, columns: List[str]) -> ValidationResult:
    """Check for duplicate rows based on the given columns."""
    rule_name = "duplicates"
    present_cols = [c for c in columns if c in df.columns]
    duplicated_mask = df.duplicated(subset=present_cols, keep=False)
    issue_count = int(duplicated_mask.sum())
    passed = issue_count == 0
    logger.info("Rule %s: passed=%s, issues=%d", rule_name, passed, issue_count)
    return ValidationResult(rule_name=rule_name, passed=passed, issue_count=issue_count)


def check_invalid_transactions(df: pd.DataFrame) -> ValidationResult:
    """Flag transactions with negative amounts (if an 'amount' column exists)."""
    rule_name = "invalid_transactions"
    if "amount" not in df.columns:
        return ValidationResult(rule_name=rule_name, passed=True, issue_count=0)
    negative_mask = df["amount"] < 0
    issue_count = int(negative_mask.sum())
    passed = issue_count == 0
    logger.info("Rule %s: passed=%s, issues=%d", rule_name, passed, issue_count)
    return ValidationResult(rule_name=rule_name, passed=passed, issue_count=issue_count)


def check_null_identifiers(df: pd.DataFrame, id_columns: List[str]) -> ValidationResult:
    """Ensure identifier columns have no null values."""
    rule_name = "null_identifiers"
    present_cols = [c for c in id_columns if c in df.columns]
    null_mask = df[present_cols].isnull().any(axis=1)
    issue_count = int(null_mask.sum())
    passed = issue_count == 0
    logger.info("Rule %s: passed=%s, issues=%d", rule_name, passed, issue_count)
    return ValidationResult(rule_name=rule_name, passed=passed, issue_count=issue_count)
