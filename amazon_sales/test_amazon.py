import pytest
import pandas as pd
from decimal import Decimal, InvalidOperation

# =====================================================================
# 1. PURE TRANSFORM FUNCTIONS (Extracted for Verification)
# =====================================================================
def clean_amazon_monetary_vector(value):
    """Safely normalizes and validates e-commerce transaction strings into Decimals."""
    if pd.isna(value) or str(value).strip() == '':
        return None
        
    price_str = str(value).strip()
    
    # Handling financial grouping and symbols automatically
    if ',' in price_str and '.' in price_str:
        price_str = price_str.replace(',', '')
    elif ',' in price_str and '.' not in price_str:
        price_str = price_str.replace(',', '.')
        
    price_str = price_str.replace('$', '').replace('€', '').strip()
    
    try:
        return Decimal(price_str)
    except InvalidOperation:
        raise ValueError(f"Financial string conversion failure for value: {value}")


# =====================================================================
# 2. PYTEST TRANSACTIONS SIMULATION (Module 5 Test suite)
# =====================================================================

@pytest.mark.parametrize("input_val, expected_output", [
    ("58,910.79", Decimal("58910.79")),
    (" $150.50 ", Decimal("150.50")),
    ("€45.00", Decimal("45.00")),
    ("", None),
])
def test_clean_amazon_monetary_vector_valid_cases(input_val, expected_output):
    """Verifies strip formatting and financial grouping symbol extraction."""
    assert clean_amazon_monetary_vector(input_val) == expected_output


def test_clean_amazon_monetary_vector_catches_syntax_faults():
    """Verifies that unparseable text payloads inside revenue metrics force hard exit code conditions."""
    with pytest.raises(ValueError, match="Financial string conversion failure for value"):
        clean_amazon_monetary_vector("CORRUPTED_MONEY_TOKEN")
