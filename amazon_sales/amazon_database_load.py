import sys
import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine

print("🚀 Starting UpDataLogic Amazon Database Ingestion Pipeline...")

# =====================================================================
# CONFIGURATION & CONNECTIONS
# =====================================================================
# Automatically locate the directory where this script is executed
BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "Amazon_sales.csv"

# Centralized DB Connection String (Placeholders to be migrated to .env in next stage)
DB_URL = 'postgresql+psycopg2://YOUR_DATABASE_USER:YOUR_DATABASE_PASSWORD@YOUR_DATABASE_HOST:5432/YOUR_DATABASE_NAME'

# =====================================================================
# ETL INGESTION STAGE
# =====================================================================
try:
    # Fail fast if the source dataset is not accessible
    if not DATA_FILE.exists():
        raise FileNotFoundError(f"Extraction halted. Source dataset missing at: {DATA_FILE}")

    print(f"📥 1. Extracting raw records from: {DATA_FILE.name}...")
    df = pd.read_csv(DATA_FILE, low_memory=False)
    
    print("⏳ 2. Sanitizing core operational metrics pre-loading...")
    df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0)
    df['Qty'] = pd.to_numeric(df['Qty'], errors='coerce').fillna(0).astype(int)
    
    print("🔌 3. Establishing connection to the remote PostgreSQL cluster...")
    engine = create_engine(DB_URL)
    
    print(f"📤 4. Injecting {len(df):,} records into production database layer ['public.amazon_sales_raw']...")
    # chunksize configuration optimizes memory consumption during massive bulk writes
    df.to_sql('amazon_sales_raw', engine, schema='public', if_exists='replace', index=False, chunksize=10000)
    
    print("\n=== 🎉 PIPELINE SUCCESS: ALL DATA PROVISIONED TO POSTGRESQL CLUSTER ===")

except Exception as e:
    # HARD FAILURE SIGNALING (UpDataLogic Rule 3)
    print(f"\n❌ PIPELINE CRITICAL FAILURE: {e}", file=sys.stderr)
    sys.exit(1)
