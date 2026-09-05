import pandas as pd
from decimal import Decimal, InvalidOperation
from typing import Any, Optional

def self_heal_amazon_amount(value: Any) -> Optional[Decimal]:
    """
    Safely normalizes and validates Amazon transactional string elements into high-precision Decimals.

    This function proactively strips local currency symbols ($, €), handles international
    alphanumeric grouping notations (commas vs dots), and extracts clean numeric slices. 
    Malformed or unparseable tokens are explicitly mapped to None to isolate them inside 
    downstream quality trackers and quarantine metrics counters.

    Args:
        value (Any): The raw currency string or numeric input slice originating from upstream systems.

    Returns:
        Optional[Decimal]: A sanitized high-precision Decimal representation for exact math, 
                           or None if critical textual data quality drift is isolated.
    """
    if pd.isna(value) or str(value).strip() == '':
        return None
        
    price_str: str = str(value).strip()
    if ',' in price_str and '.' in price_str:
        price_str = price_str.replace(',', '')
    elif ',' in price_str and '.' not in price_str:
        price_str = price_str.replace(',', '.')
        
    price_str = price_str.replace('$', '').replace('€', '').strip()
    
    try:
        return Decimal(price_str)
    except InvalidOperation:
        return None  # Maps to strict None (NULL) to trigger operational metrics counters
