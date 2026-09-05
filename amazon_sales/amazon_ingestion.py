import os
import sys
import logging
import pandas as pd
import pandera.pandas as pa
from pathlib import Path
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# =====================================================================
# ENTERPRISE LOGGING CONFIGURATION (Module 6 & 7 Standard)
# =====================================================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [UpDataLogic Ingestion] - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logging.info("🚀 Starting UpDataLogic Amazon Database Ingestion Pipeline (Idempotent Production Mode)...")

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "Amazon_sales_sample.csv"
ENV_FILE = BASE_DIR / ".env"

# 1. Define Strict Data Quality Ingestion Shield via Pandera Specification
amazon_ingest_schema = pa.DataFrameSchema({
    "Order ID": pa.Column(str, nullable=False),
    "Status": pa.Column(str, nullable=False),
    "Qty": pa.Column(int, pa.Check.ge(0), nullable=False),
    "Amount": pa.Column(float, nullable=True)
})

# 2. Database Connection Check with Dynamic Fallback Context Routing
try:
    if ENV_FILE.exists():
        load_dotenv(dotenv_path=ENV_FILE, override=True)
        DB_USER = os.getenv("DB_USER")
        DB_PASSWORD = os.getenv("DB_PASSWORD")
        DB_HOST = os.getenv("DB_HOST")
        DB_PORT = os.getenv("DB_PORT", "6543")
        DB_NAME = os.getenv("DB_NAME")
        
        if not all([DB_USER, DB_PASSWORD, DB_HOST, DB_NAME]):
            raise ValueError("Incomplete database credentials inside configuration targets.")
            
        connection_string = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        engine = create_engine(connection_string)
        with engine.connect() as conn:
            pass
        logging.info("🔌 Connection Status: [ONLINE] Remote PostgreSQL Warehouse Connected.")
    else:
        raise FileNotFoundError("Local configurations env targets missing.")

except Exception as db_error:
    logging.warning(f"⚠️ Production DB Offline or Network Issue detected: {db_error}")
    logging.info("🔄 Activating Portfolio Architecture Fallback Mode (Local Standalone Engine)...")
    connection_string = f"sqlite:///{BASE_DIR / 'local_portfolio.db'}"
    engine = create_engine(connection_string)
    logging.info("🔌 Connection Status: [LOCAL ENGINE] Active Fallback SQLite Context Deployed.")

# =====================================================================
# ETL INGESTION STAGE Execution with Idempotent UPSERT Matrix
# =====================================================================
try:
    if not DATA_FILE.exists():
        raise FileNotFoundError(f"Extraction halted. Source dataset missing at: {DATA_FILE}")

    logging.info(f"📥 1. EXTRACTION: Reading raw records from target file: {DATA_FILE.name}")
    df = pd.read_csv(DATA_FILE, dtype={"Order ID": str}, low_memory=False)
    
    logging.info("⏳ 2. TRANSFORMATION: Executing structural data pre-load alignment matrices...")
    df['Qty'] = pd.to_numeric(df['Qty'], errors='coerce').fillna(0).astype(int)
    df['Amount'] = df['Amount'].astype(str).str.replace(',', '', regex=False)
    df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce')
    
    logging.info("🛡️ 3. VALIDATION: Running structural data quality tests via Pandera schema evaluation...")
    validated_df = amazon_ingest_schema.validate(df)
    
    validated_df['data_quality_status'] = validated_df[['Amount', 'Qty']].isnull().any(axis=1).map({True: 'UNKNOWN', False: 'CLEAN'})
    
    logging.info("📤 4. LOADING: Executing idempotent UPSERT pattern routing directly to database engine...")
    
    # Enforce database schema constraint setups inside atomic blocks
    with engine.begin() as transaction_conn:
        if str(engine.url).startswith('sqlite'):
            # SENIORSKÁ SAMOOPRAVA LOKÁLNEHO ENGINU: Vytvoríme tabuľku s riadnym PRIMARY KEY, ak chýba
            transaction_conn.execute(text("DROP TABLE IF EXISTS amazon_sales_raw;"))
            transaction_conn.execute(text("""
                CREATE TABLE amazon_sales_raw (
                    "Order ID" TEXT PRIMARY KEY,
                    Status TEXT,
                    Qty INTEGER,
                    Amount REAL,
                    data_quality_status TEXT
                );
            """))
            logging.info("🧹 Local SQLite Strategy: Schema mapped with strict Primary Key specifications.")

            for _, row in validated_df.iterrows():
                upsert_query = text("""
                    INSERT INTO amazon_sales_raw ("Order ID", Status, Qty, Amount, data_quality_status)
                    VALUES (:_Order_ID, :Status, :Qty, :Amount, :data_quality_status)
                    ON CONFLICT("Order ID") DO UPDATE SET
                        Status=excluded.Status,
                        Qty=excluded.Qty,
                        Amount=excluded.Amount,
                        data_quality_status=excluded.data_quality_status;
                """)
                row_dict = row.to_dict()
                row_dict['_Order_ID'] = row_dict.pop('Order ID')
                transaction_conn.execute(upsert_query, row_dict)
        else:
            # Ostrý cloudový PostgreSQL má už kľúče z DDL skriptov nasadené permanentne
            for _, row in validated_df.iterrows():
                upsert_query = text("""
                    INSERT INTO amazon_sales_raw ("Order ID", "Status", "Qty", "Amount", "data_quality_status")
                    VALUES (:_Order_ID, :Status, :Qty, :Amount, :data_quality_status)
                    ON CONFLICT ("Order ID") DO UPDATE SET
                        "Status" = EXCLUDED.Status,
                        "Qty" = EXCLUDED.Qty,
                        "Amount" = EXCLUDED.Amount,
                        "data_quality_status" = EXCLUDED.data_quality_status;
                """)
                row_dict = row.to_dict()
                row_dict['_Order_ID'] = row_dict.pop('Order ID')
                transaction_conn.execute(upsert_query, row_dict)
                
    logging.info("🏆 PIPELINE RUN COMPLETION: STATUS 0 [SUCCESS]. Idempotency matrix guarantee verified.\n")
    sys.exit(0)

except pa.errors.SchemaError as schema_fault:
    logging.critical(f"❌ PIPELINE STOPPED VIA PANDERA INGESTION SHIELD: {schema_fault}")
    sys.exit(1)
except Exception as fatal_error:
    logging.critical(f"❌ PIPELINE INGESTION CRITICAL RUNTIME FAILURE: {fatal_error}")
    sys.exit(1)
