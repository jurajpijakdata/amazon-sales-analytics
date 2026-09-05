import os
import sys
import logging
import pandas as pd
import pandera.pandas as pa
from pathlib import Path

# Import the decoupled tested business function from our clean parser module
from amazon_parser import self_heal_amazon_amount

# =====================================================================
# ENTERPRISE LOGGING CONFIGURATION (Module 6 Standard)
# =====================================================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [UpDataLogic Amazon Engine] - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logging.info("🚀 Starting UpDataLogic Amazon Sales Analytics Engine (Production Observability Mode)...")

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "Amazon_sales_sample.csv"

# First-class operation metrics trackers for alerting thresholds
METRICS_TRACKER = {
    "total_records_extracted": 0,
    "successfully_healed_records": 0,
    "rejected_records_critical": 0
}

# 1. DECLARATIVE DATA QUALITY SCHEMA SHIELD (Pandera Specification)
amazon_schema = pa.DataFrameSchema({
    "Order ID": pa.Column(str, nullable=False),
    "Status": pa.Column(str, nullable=False),
    "Qty": pa.Column(int, pa.Check.ge(0), nullable=False),
    "Amount_Decimal": pa.Column(float, nullable=True),
})

# DATA PIPELINE EXECUTION WITH MONITORING
try:
    if not DATA_FILE.exists():
        raise FileNotFoundError(f"Critical data resource not found at expected location: {DATA_FILE}")
        
    logging.info(f"📥 1. EXTRACTION: Loading raw Amazon transactional dataset: {DATA_FILE.name}")
    df = pd.read_csv(DATA_FILE, dtype={"Order ID": str}, low_memory=False)
    
    METRICS_TRACKER["total_records_extracted"] = len(df)
    logging.info(f"✅ EXTRACTION SUCCESS: Pulled {METRICS_TRACKER['total_records_extracted']:,} transactional logs into high-performance memory.")
    
    logging.info("⏳ 2. TRANSFORMATION: Executing self-healing financial parsing layers...")
    
    # Process financial metrics through the decoupled parser matrix row-by-row
    df['Amount_Decimal_Obj'] = df['Amount'].apply(self_heal_amazon_amount)
    df['Amount_Decimal'] = df['Amount_Decimal_Obj'].apply(lambda x: float(x) if x is not None else None)
    df['Qty'] = pd.to_numeric(df['Qty'], errors='coerce').fillna(0).astype(int)

    logging.info("🛡️ 3. VALIDATION: Running declarative data quality checks via Pandera schema evaluation...")
    validated_df = amazon_schema.validate(df)
    
    # Separate quality status isolation matrix (sibling column mapping)
    validated_df['data_quality_status'] = validated_df['Amount_Decimal'].apply(lambda x: 'CLEAN' if x is not None else 'UNKNOWN')
    
    # Audit metrics computation
    METRICS_TRACKER["rejected_records_critical"] = int(validated_df['Amount_Decimal'].isna().sum())
    METRICS_TRACKER["successfully_healed_records"] = METRICS_TRACKER["total_records_extracted"] - METRICS_TRACKER["rejected_records_critical"]
    
    rejection_rate = (METRICS_TRACKER["rejected_records_critical"] / METRICS_TRACKER["total_records_extracted"]) * 100
    logging.info(f"📊 DATA QUALITY METRICS: Clean/Healed: {METRICS_TRACKER['successfully_healed_records']:,} | Quarantined/NULL: {METRICS_TRACKER['rejected_records_critical']:,} ({rejection_rate:.2f}%)")
    
    # Alerting threshold boundaries execution layer (Fail-fast principle rule)
    if rejection_rate > 5.0:
        raise ValueError(f"Pipeline stopped. Rejection rate {rejection_rate:.2f}% breached production threshold limit (5.0%)")
        
    logging.info("\n=== 🎉 DATA VALIDATION & CLEANSING COMPLETED SUCCESSFULLY ===")
    clean_numeric_df = validated_df[validated_df['data_quality_status'] == 'CLEAN']
    
    gross_revenue = sum(clean_numeric_df['Amount_Decimal_Obj'].dropna())
    logging.info(f"Total Gross Revenue: {float(gross_revenue):,.2f} EUR")
    
    invalid_statuses = ['Cancelled', 'Shipped - Returned to Seller', 'Returned']
    clean_cashflow_df = clean_numeric_df[~clean_numeric_df['Status'].isin(invalid_statuses)]
    
    net_revenue = sum(clean_cashflow_df['Amount_Decimal_Obj'].dropna())
    logging.info(f"Total Net Revenue (Clean Cashflow): {float(net_revenue):,.2f} EUR")
    print("=" * 60)
    
    logging.info("🏆 PIPELINE PROCESS COMPLETION: STATUS 0 [SUCCESS]. Financial telemetry secured successfully.\n")
    sys.exit(0) # Clean scheduler telemetry indicator

except pa.errors.SchemaError as schema_fault:
    logging.critical(f"❌ PIPELINE STOPPED VIA PANDERA STRUCTURAL SHIELD: {schema_fault}")
    sys.exit(1) # Enforce exit 1 code configurations for orchstrators
except Exception as fatal_error:
    logging.critical(f"❌ PIPELINE CRITICAL RUNTIME FAILURE: {fatal_error}")
    sys.exit(1)
