import pandas as pd
import pytest
from src.validation.rules import check_missing_values, check_duplicates, check_invalid_transactions, check_null_identifiers

# Sample dataframe for PaySim-like data
@pytest.fixture
def paysim_df():
    data = {
        "step": [1, 2, 3],
        "type": [0, 1, 0],
        "amount": [100.0, -5.0, 200.0],  # one invalid negative amount
        "nameOrig": ["C123", "C124", None],  # one null identifier
        "nameDest": ["M123", "M124", "M125"],
        "oldbalanceOrg": [1000, 2000, 3000],
        "newbalanceOrig": [900, 1995, 2800],
        "oldbalanceDest": [5000, 6000, 7000],
        "newbalanceDest": [5100, 6105, 7200],
        "isFraud": [0, 0, 0],
        "isFlaggedFraud": [0, 0, 0],
    }
    return pd.DataFrame(data)

def test_missing_values(paysim_df):
    result = check_missing_values(paysim_df, ["step", "type", "amount", "nameOrig", "nameDest"])
    assert not result.passed
    assert result.issue_count == 1  # one row has missing nameOrig

def test_duplicates(paysim_df):
    # Duplicate a row deliberately
    df_dup = pd.concat([paysim_df, paysim_df.iloc[[0]]], ignore_index=True)
    result = check_duplicates(df_dup, ["step", "type", "amount", "nameOrig", "nameDest"])
    assert not result.passed
    # Two rows are duplicates (original and appended)
    assert result.issue_count == 2

def test_invalid_transactions(paysim_df):
    result = check_invalid_transactions(paysim_df)
    assert not result.passed
    assert result.issue_count == 1  # one negative amount

def test_null_identifiers(paysim_df):
    result = check_null_identifiers(paysim_df, ["nameOrig", "nameDest"])
    assert not result.passed
    assert result.issue_count == 1
