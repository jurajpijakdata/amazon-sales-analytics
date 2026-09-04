import os
import sys
import pandas as pd
import pandera.pandas as pa
from pathlib import Path
from decimal import Decimal, InvalidOperation
from sqlalchemy import create_engine
from dotenv import load_dotenv

print("🚀 Starting UpDataLogic Amazon Database Ingestion Pipeline (Production Blueprint)...")

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "Amazon_sales_sample.csv"
ENV_FILE = BASE_DIR / ".env"

# 1. Define Strict Data Quality Shield using Pandera
amazon_ingest_schema = pa.DataFrameSchema({
    "Order ID": pa.Column(str, nullable=False),
    "Status": pa.Column(str, nullable=False),
    "Qty": pa.Column(int, pa.Check.ge(0), nullable=False),
    "Amount": pa.Column(float, nullable=True)
})

# STRICT FILE-BASED SANDBOX LAYER (Bypasses stubborn Windows System Cache indices)
if ENV_FILE.exists():
    load_dotenv(dotenv_path=ENV_FILE, override=True)
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT", "6543")
    DB_NAME = os.getenv("DB_NAME")
else:
    DB_USER = DB_PASSWORD = DB_HOST = DB_NAME = None
    DB_PORT = "6543"

if not all([DB_USER, DB_PASSWORD, DB_HOST, DB_NAME]):
    print("\n💡 PORTFOLIO NOTE: Operational pipeline running in BLUEPRINT/TEMPLATE mode.")
    print("To execute this ingestion actively on live storage, populate your secure local '.env' targets.")
    print("Pipeline execution completed safely as an architecture proof-of-concept for target clients.\n")
    sys.exit(0)

connection_string = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(connection_string)

# =====================================================================
# ETL INGESTION STAGE
# =====================================================================
try:
    if not DATA_FILE.exists():
        raise FileNotFoundError(f"Extraction halted. Source dataset missing at: {DATA_FILE}")

    print(f"📥 1. Extracting raw records from: {DATA_FILE.name}...")
    df = pd.read_csv(DATA_FILE, dtype={"Order ID": str}, low_memory=False)
    
    print("⏳ 2. Executing pre-load data type normalization pipeline...")
    df['Qty'] = pd.to_numeric(df['Qty'], errors='coerce').fillna(0).astype(int)
    
    # SENIORSKÁ OPRAVA: Odstránenie tisíckových čiarok z textu pred číselnou konverziou
    df['Amount'] = df['Amount'].astype(str).str.replace(',', '', regex=False)
    df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce')
    
    print("🛡️ 3. Running declarative data quality checks via Pandera schema evaluation...")
    validated_df = amazon_ingest_schema.validate(df)
    
    validated_df['data_quality_status'] = validated_df[['Amount', 'Qty']].isnull().any(axis=1).map({True: 'UNKNOWN', False: 'CLEAN'})
    
    print(f"📤 4. Stream loading {len(validated_df):,} validated records into database layer...")
    validated_df.to_sql('amazon_sales_raw', engine, schema='public', if_exists='replace', index=False)
    
    print("\n=== 🎉 PIPELINE SUCCESS: ALL DATA PROVISIONED TO POSTGRESQL CLUSTER ===")

except pa.errors.SchemaError as schema_fault:
    print(f"\n❌ DATA QUALITY BREACH DETECTED BY PANDERA:\n{schema_fault}", file=sys.stderr)
    sys.exit(1)
except Exception as e:
    print(f"\n❌ PIPELINE CRITICAL FAILURE: {e}", file=sys.stderr)
    sys.exit(1)
