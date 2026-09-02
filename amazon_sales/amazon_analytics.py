import sys
import pandas as pd
from pathlib import Path

print("🚀 Starting UpDataLogic Amazon Sales Analytics Engine...")

# =====================================================================
# DYNAMIC PATH RESOLUTION (UpDataLogic Rule 2)
# =====================================================================
# Automatically locate the directory where this script is executed
BASE_DIR = Path(__file__).resolve().parent

# Dynamically build the path to target the correct folder and casing
DATA_FILE = BASE_DIR / "Amazon_sales.csv"

# =====================================================================
# DATA PIPELINE EXECUTION
# =====================================================================
try:
    # Fail fast if the required dataset is missing from the environment
    if not DATA_FILE.exists():
        raise FileNotFoundError(f"Critical data resource not found at expected location: {DATA_FILE}")
        
    print(f"📥 Loading dataset: {DATA_FILE.name}...")
    df = pd.read_csv(DATA_FILE, low_memory=False)
    
    # 1. Clean the financial metrics
    df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0)
    
    # 2. Inspect order taxonomy
    print("\n=== UNIQUE ORDER STATUSES IN DATASET ===")
    print(df['Status'].unique())
    
    # 3. Financial Performance Audit
    print("\n=== GROSS VS NET REVENUE ANALYSIS ===")
    gross_revenue = df['Amount'].sum()
    print(f"Total Gross Revenue: {gross_revenue:,.2f}")
    
    # Filter out compromised transaction statuses to isolate clean cash flow
    invalid_statuses = ['Cancelled', 'Shipped - Returned to Seller', 'Returned']
    clean_df = df[~df['Status'].isin(invalid_statuses)]
    
    net_revenue = clean_df['Amount'].sum()
    print(f"Total Net Revenue (Clean): {net_revenue:,.2f}")
    
    # Quantify revenue leak due to logistics cancellations
    revenue_lost = gross_revenue - net_revenue
    print(f"Total Revenue Lost Due to Cancellations/Returns: {revenue_lost:,.2f}")
    print("\n🏆 ANALYTICS RUN COMPLETED SUCCESSFULLY.")

except Exception as e:
    # HARD FAILURE SIGNALING (UpDataLogic Rule 3)
    print(f"\n❌ PIPELINE CRITICAL FAILURE: {e}", file=sys.stderr)
    sys.exit(1)
