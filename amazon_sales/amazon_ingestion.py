import os
import sys
import pandas as pd
from pathlib import Path
from decimal import Decimal, InvalidOperation
from sqlalchemy import create_engine
from dotenv import load_dotenv

print("🚀 Starting UpDataLogic Amazon Database Ingestion Pipeline (Production Blueprint)...")

# Initialize isolated local configuration environment lookups
load_dotenv(override=True)

# =====================================================================
# CONFIGURATION & CONNECTIONS (Dynamic Gateway Sourcing)
# =====================================================================
BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "Amazon_sales_sample.csv"

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "6543") # Pre-configured for connection pooler layers
DB_NAME = os.getenv("DB_NAME")

# Multi-Mode Sandbox Selection Strategy
if not all([DB_USER, DB_PASSWORD, DB_HOST, DB_NAME]):
    print("\n💡 PORTFOLIO NOTE: Operational pipeline running in BLUEPRINT/TEMPLATE mode.")
    print("To execute this ingestion actively on live storage, populate your secure local '.env' targets.")
    print("Pipeline execution completed safely as an architecture proof-of-concept for target clients.\n")
    sys.exit(0)

# Build infrastructure connection string parameters
DB_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# =====================================================================
# ETL INGESTION STAGE
# =====================================================================
try:
    if not DATA_FILE.exists():
        raise FileNotFoundError(f"Extraction halted. Source dataset missing at: {DATA_FILE}")

    print(f"📥 1. Extracting raw records from: {DATA_FILE.name}...")
    df = pd.read_csv(DATA_FILE, low_memory=False)
    
    print("⏳ 2. Executing pre-load data type normalization pipeline...")
    all_metrics = ['Amount', 'Qty']
    
    def strict_numeric_normalizer(value):
        if pd.isna(value) or str(value).strip() == '':
            return None
        clean_str = str(value).strip().replace(',', '.')
        try:
            return float(Decimal(clean_str).quantize(Decimal("0.01")))
        except InvalidOperation:
            return None

    def strict_qty_normalizer(value):
        if pd.isna(value) or str(value).strip() == '':
            return None
        try:
            return int(float(str(value).strip()))
        except (ValueError, TypeError):
            return None

    # Protect downstream averages by avoiding raw array zero-interpolations (.fillna)
    df['Amount'] = df['Amount'].apply(strict_numeric_normalizer)
    df['Qty'] = df['Qty'].apply(strict_qty_normalizer)
    
    # Map explicit structure validation tracking vectors
    df['data_quality_status'] = df[['Amount', 'Qty']].isnull().any(axis=1).map({True: 'UNKNOWN', False: 'CLEAN'})
    
    print("🔌 3. Establishing connection to the remote PostgreSQL cluster...")
    engine = create_engine(DB_URL)
    
    print(f"📤 4. Stream loading {len(df):,} records into database target ['public.amazon_sales_raw']...")
    # Stream data chunks to defend remote target server memory thresholds
    df.to_sql('amazon_sales_raw', engine, schema='public', if_exists='replace', index=False, chunksize=10000)
    
    print("\n=== 🎉 PIPELINE SUCCESS: ALL DATA PROVISIONED TO POSTGRESQL CLUSTER ===")

except Exception as e:
    print(f"\n❌ PIPELINE CRITICAL FAILURE: {e}", file=sys.stderr)
    sys.exit(1)
