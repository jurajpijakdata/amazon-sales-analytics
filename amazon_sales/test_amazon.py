import pytest
from decimal import Decimal
# Import the actual pure production logic module to avoid duplicates
from amazon_parser import self_heal_amazon_amount

@pytest.mark.parametrize("input_val, expected_output", [
    ("58,910.79", Decimal("58910.79")),
    (" $150.50 ", Decimal("150.50")),
    ("€45.00", Decimal("45.00")),
    ("", None),
])
def test_clean_amazon_monetary_vector_valid_cases(input_val, expected_output):
    """Verifies strip formatting and financial grouping symbol extraction."""
    assert self_heal_amazon_amount(input_val) == expected_output


def test_clean_amazon_monetary_vector_catches_syntax_faults():
    """Verifies that unparseable text payloads return None safely for tracking metrics."""
    assert self_heal_amazon_amount("CORRUPTED_MONEY_TOKEN") is None
