import os
import sys
import re
import pandas as pd
from pathlib import Path
from decimal import Decimal, InvalidOperation

print("🚀 Starting UpDataLogic Amazon Sales Analytics Engine (Enhanced Financial Integrity)...")

# =====================================================================
# DYNAMIC PATH RESOLUTION (Cross-Platform Execution Compatibility)
# =====================================================================
BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "Amazon_sales_sample.csv"

# =====================================================================
# DATA PIPELINE EXECUTION
# =====================================================================
try:
    if not DATA_FILE.exists():
        raise FileNotFoundError(f"Critical data resource not found at expected location: {DATA_FILE}")
        
    print(f"📥 Loading dataset: {DATA_FILE.name}...")
    df = pd.read_csv(DATA_FILE, low_memory=False)
    
    print("\n⏳ Executing strict Amazon financial parsing pipeline...")
    
    # High-precision token parser to completely eliminate binary float drifting
    def clean_amazon_amount(value):
        if pd.isna(value) or str(value).strip() == '':
            return None # Missing monetary values map purely to clean NULL states
            
        price_str = str(value).strip().replace(',', '.')
        price_str = price_str.replace('$', '').replace('€', '').strip()
        
        # Regular expression validation to secure formatting patterns
        match = re.match(r"^-?\d+(?:\.\d+)?$", price_str)
        if not match:
            return None
            
        try:
            return Decimal(price_str)
        except InvalidOperation:
            return None

    # Cast metrics into strict high-precision Decimal objects
    df['Amount_Decimal'] = df['Amount'].apply(clean_amazon_amount)
    
    # Decouple quality metrics from primary measure vectors to preserve data types
    df['data_quality_status'] = df['Amount_Decimal'].apply(lambda x: 'CLEAN' if x is not None else 'UNKNOWN')
    
    print("\n=== UNIQUE ORDER STATUSES IN DATASET ===")
    print(df['Status'].unique())
    
    print("\n=== GROSS VS NET REVENUE ANALYSIS (FINANCIAL AUDIT COMPLIANT) ===")
    
    # Isolate valid verified data points for auditing aggregates
    clean_numeric_df = df[df['data_quality_status'] == 'CLEAN']
    
    gross_revenue = sum(clean_numeric_df['Amount_Decimal'])
    print(f"Total Gross Revenue: {float(gross_revenue):,.2f} EUR")
    
    # Filter out reversed and unfulfilled transaction logs to isolate core cash flow
    invalid_statuses = ['Cancelled', 'Shipped - Returned to Seller', 'Returned']
    clean_cashflow_df = clean_numeric_df[~clean_numeric_df['Status'].isin(invalid_statuses)]
    
    net_revenue = sum(clean_cashflow_df['Amount_Decimal'])
    print(f"Total Net Revenue (Clean): {float(net_revenue):,.2f} EUR")
    
    # Calculate revenue leak intervals across logistical returns
    revenue_lost = gross_revenue - net_revenue
    print(f"Total Revenue Lost Due to Cancellations/Returns: {float(revenue_lost):,.2f} EUR")
    print("\n🏆 ANALYTICS RUN COMPLETED SUCCESSFULLY.")

except Exception as e:
    print(f"\n❌ PIPELINE CRITICAL FAILURE: {e}", file=sys.stderr)
    sys.exit(1)
