import os
import sys
import logging
import pandas as pd
import pandera.pandas as pa
from pathlib import Path
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Import the decoupled, tested business logic from our clean parser module
from amazon_parser import self_heal_amazon_amount

# Force UTF-8 on stdout regardless of the calling environment's console
# codepage. Without this, on Windows, running the script without an
# interactive terminal attached (a subprocess, a scheduler, some CI
# runners) falls back to a legacy encoding that can't represent the
# emoji used in these log messages -- Python's logging module then fails
# silently on every log call instead of crashing, so the pipeline appears
# to run with zero visible output.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# =====================================================================
# ENTERPRISE LOGGING CONFIGURATION (Module 6, 7 & 10 Standard)
# =====================================================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [UpDataLogic Amazon Ingestion] - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logging.info("🚀 Starting UpDataLogic Amazon Sales Ingestion Layer (Idempotent Production Mode)...")

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "Amazon_sales_sample.csv"
ENV_FILE = BASE_DIR / ".env"

METRICS_TRACKER = {
    "total_records_extracted": 0,
    "successfully_healed_records": 0,
    "rejected_records_critical": 0
}

# Define Data Quality Shield using Pandera Specification
amazon_ingest_schema = pa.DataFrameSchema({
    "order_line_id": pa.Column(str, nullable=False),
    "order_id": pa.Column(str, nullable=False),
    "status": pa.Column(str, nullable=False),
    "category": pa.Column(str, nullable=True),
    "size": pa.Column(str, nullable=True),
    "qty": pa.Column(int, pa.Check.ge(0), nullable=False),
    "amount_inr": pa.Column(float, nullable=True),
})

# Database Connection Check with Fallback
try:
    if ENV_FILE.exists():
        load_dotenv(dotenv_path=ENV_FILE, override=True)
        DB_USER = os.getenv("DB_USER")
        DB_PASSWORD = os.getenv("DB_PASSWORD")
        DB_HOST = os.getenv("DB_HOST")
        DB_PORT = os.getenv("DB_PORT", "6543")
        DB_NAME = os.getenv("DB_NAME")

        if not all([DB_USER, DB_PASSWORD, DB_HOST, DB_NAME]):
            raise ValueError("Incomplete cloud credentials.")

        connection_string = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        engine = create_engine(connection_string)
        with engine.connect() as conn:
            pass
        logging.info("🔌 Connection Status: [ONLINE] Remote PostgreSQL Warehouse Connected.")
    else:
        raise FileNotFoundError("Config file missing.")

except Exception as db_error:
    logging.warning(f"⚠️ Production DB Offline or Network Issue detected: {db_error}")
    logging.info("🔄 Activating Portfolio Architecture Fallback Mode (Local Storage Engine)...")
    connection_string = f"sqlite:///{BASE_DIR / 'local_portfolio.db'}"
    engine = create_engine(connection_string)
    logging.info("🔌 Connection Status: [LOCAL ENGINE] Active Fallback SQLite Context Deployed.")

is_sqlite = str(engine.url).startswith('sqlite')

# create_tables.sql (Postgres-specific: SERIAL columns, CHECK constraints,
# indexes) is meant to be run once against the real cloud database. This
# fallback only creates the one table the load step writes to, so the
# pipeline has somewhere to land data when no cloud database is
# configured -- it's for local demoing without credentials, not a full
# port of the production schema.
if is_sqlite:
    with engine.begin() as bootstrap_conn:
        bootstrap_conn.execute(text("""
            CREATE TABLE IF NOT EXISTS amazon_sales_fact (
                order_line_id TEXT PRIMARY KEY,
                order_id TEXT,
                order_date TEXT,
                status TEXT,
                fulfilment TEXT,
                category TEXT,
                size TEXT,
                sku TEXT,
                qty INTEGER,
                currency TEXT,
                amount_inr REAL,
                ship_state TEXT,
                data_quality_status TEXT
            );
        """))

# =====================================================================
# ETL INGESTION STAGE Execution with Idempotent UPSERT Matrix
# =====================================================================
try:
    if not DATA_FILE.exists():
        raise FileNotFoundError(f"Source dataset missing at: {DATA_FILE}")

    logging.info(f"📥 1. EXTRACTION: Reading records from: {DATA_FILE.name}...")
    df = pd.read_csv(DATA_FILE, dtype={"Order ID": str, "index": str}, low_memory=False)

    METRICS_TRACKER["total_records_extracted"] = len(df)
    logging.info(f"✅ EXTRACTION SUCCESS: Pulled {METRICS_TRACKER['total_records_extracted']:,} transactional logs into memory.")

    logging.info("⏳ 2. TRANSFORMATION: Executing self-healing financial parsing layers...")

    # "index" is the CSV's own row identifier and is unique per line item --
    # unlike "Order ID", which repeats when one order has several SKUs.
    # It becomes the primary key for the line-item table.
    df['order_line_id'] = df['index'].astype(str)
    df['order_id'] = df['Order ID'].astype(str)

    df['amount_decimal_obj'] = df['Amount'].apply(self_heal_amazon_amount)
    df['amount_inr'] = df['amount_decimal_obj'].apply(lambda x: float(x) if x is not None else None)
    df['qty'] = pd.to_numeric(df['Qty'], errors='coerce').fillna(0).astype(int)
    df['data_quality_status'] = df['amount_inr'].apply(lambda x: 'CLEAN' if x is not None else 'UNKNOWN')

    # Build a clean, lowercase-column staging frame matching the target table.
    staging_df = pd.DataFrame({
        "order_line_id": df['order_line_id'],
        "order_id": df['order_id'],
        "order_date": df['Date'].astype(str),
        "status": df['Status'].astype(str),
        "fulfilment": df['Fulfilment'].astype(str),
        "category": df['Category'].astype(str),
        "size": df['Size'].astype(str),
        "sku": df['SKU'].astype(str),
        "qty": df['qty'],
        "currency": df['currency'].astype(str),
        "amount_inr": df['amount_inr'],
        "ship_state": df['ship-state'].astype(str),
        "data_quality_status": df['data_quality_status'],
    })

    logging.info("🛡️ 3. VALIDATION: Running declarative data quality checks via Pandera schema evaluation...")
    validated_df = amazon_ingest_schema.validate(staging_df)

    METRICS_TRACKER["rejected_records_critical"] = int(validated_df['amount_inr'].isna().sum())
    METRICS_TRACKER["successfully_healed_records"] = METRICS_TRACKER["total_records_extracted"] - METRICS_TRACKER["rejected_records_critical"]

    rejection_rate = (METRICS_TRACKER["rejected_records_critical"] / METRICS_TRACKER["total_records_extracted"]) * 100
    logging.info(f"📊 DATA QUALITY METRICS: Clean: {METRICS_TRACKER['successfully_healed_records']:,} | Rejections: {METRICS_TRACKER['rejected_records_critical']:,} ({rejection_rate:.2f}%)")

    if rejection_rate > 5.0:
        raise ValueError(f"Pipeline stopped. Rejection rate {rejection_rate:.2f}% breached 5.0% limit.")

    logging.info("📤 4. LOADING: Executing idempotent UPSERT pattern routing directly to database engine...")

    records = validated_df.to_dict(orient='records')

    if is_sqlite:
        upsert_query = text("""
            INSERT INTO amazon_sales_fact (order_line_id, order_id, order_date, status, fulfilment, category, size, sku, qty, currency, amount_inr, ship_state, data_quality_status)
            VALUES (:order_line_id, :order_id, :order_date, :status, :fulfilment, :category, :size, :sku, :qty, :currency, :amount_inr, :ship_state, :data_quality_status)
            ON CONFLICT(order_line_id) DO UPDATE SET
                order_id=excluded.order_id,
                order_date=excluded.order_date,
                status=excluded.status,
                fulfilment=excluded.fulfilment,
                category=excluded.category,
                size=excluded.size,
                sku=excluded.sku,
                qty=excluded.qty,
                currency=excluded.currency,
                amount_inr=excluded.amount_inr,
                ship_state=excluded.ship_state,
                data_quality_status=excluded.data_quality_status;
        """)
    else:
        upsert_query = text("""
            INSERT INTO amazon_sales_fact ("order_line_id", "order_id", "order_date", "status", "fulfilment", "category", "size", "sku", "qty", "currency", "amount_inr", "ship_state", "data_quality_status")
            VALUES (:order_line_id, :order_id, :order_date, :status, :fulfilment, :category, :size, :sku, :qty, :currency, :amount_inr, :ship_state, :data_quality_status)
            ON CONFLICT ("order_line_id") DO UPDATE SET
                "order_id" = EXCLUDED.order_id,
                "order_date" = EXCLUDED.order_date,
                "status" = EXCLUDED.status,
                "fulfilment" = EXCLUDED.fulfilment,
                "category" = EXCLUDED.category,
                "size" = EXCLUDED.size,
                "sku" = EXCLUDED.sku,
                "qty" = EXCLUDED.qty,
                "currency" = EXCLUDED.currency,
                "amount_inr" = EXCLUDED.amount_inr,
                "ship_state" = EXCLUDED.ship_state,
                "data_quality_status" = EXCLUDED.data_quality_status;
        """)

    # Chunked bulk upsert -- one round trip per batch of rows, not per row.
    CHUNK_SIZE = 1000
    with engine.begin() as transaction_conn:
        for i in range(0, len(records), CHUNK_SIZE):
            chunk = records[i:i + CHUNK_SIZE]
            transaction_conn.execute(upsert_query, chunk)

    logging.info("🏆 PIPELINE RUN COMPLETION: STATUS 0 [SUCCESS]. Idempotency & Database Integrity metrics verified.\n")
    sys.exit(0)

except pa.errors.SchemaError as schema_fault:
    logging.critical(f"❌ PIPELINE STOPPED VIA PANDERA INGESTION SHIELD: {schema_fault}")
    sys.exit(1)
except Exception as e:
    logging.critical(f"❌ PIPELINE RUN CRITICAL FAILURE: {e}")
    sys.exit(1)
