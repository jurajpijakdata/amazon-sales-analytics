import pandas as pd
from decimal import Decimal, InvalidOperation

def self_heal_amazon_amount(value):
    """
    Safely normalizes and validates Amazon transactional string elements into high-precision Decimals.
    Strips currency signs, white spaces, and decimal variations.
    Returns Decimal objects or None for malformed tokens to isolate in data quality metrics counters.
    """
    if pd.isna(value) or str(value).strip() == '':
        return None
        
    price_str = str(value).strip()
    if ',' in price_str and '.' in price_str:
        price_str = price_str.replace(',', '')
    elif ',' in price_str and '.' not in price_str:
        price_str = price_str.replace(',', '.')
        
    price_str = price_str.replace('$', '').replace('€', '').strip()
    
    try:
        return Decimal(price_str)
    except InvalidOperation:
        return None  # Maps to strict None (NULL) to trigger operational metrics counters
