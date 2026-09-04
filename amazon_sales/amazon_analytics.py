import os
import sys
import pandas as pd
import pandera.pandas as pa
from pathlib import Path
from decimal import Decimal, InvalidOperation

print("🚀 Starting UpDataLogic Amazon Sales Analytics Engine (Self-Healing & Validated)...")

# =====================================================================
# DYNAMIC PATH RESOLUTION
# =====================================================================
BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "Amazon_sales_sample.csv"

# =====================================================================
# 1. DECLARATIVE DATA QUALITY SCHEMA (The Ultimate Safety Shield)
# =====================================================================
amazon_schema = pa.DataFrameSchema({
    "Order ID": pa.Column(str, nullable=False), # Must be text
    "Status": pa.Column(str, nullable=False),
    "Qty": pa.Column(int, pa.Check.ge(0), nullable=False),
    "Amount_Decimal": pa.Column(float, nullable=True), # Clean parsed floating points for reporting
})

# =====================================================================
# DATA PIPELINE EXECUTION
# =====================================================================
try:
    if not DATA_FILE.exists():
        raise FileNotFoundError(f"Critical data resource not found at expected location: {DATA_FILE}")
        
    print(f"📥 Loading dataset: {DATA_FILE.name}...")
    
    # SAMOOPRAVNÉ NAČÍTANIE: Vynútime textový formát pre Order ID, aj keby ho systém poslal ako čisté číslo!
    df = pd.read_csv(DATA_FILE, dtype={"Order ID": str}, low_memory=False)
    
    print("\n⏳ Executing self-healing financial parsing layer...")
    
    # Samoopravná funkcia: automaticky čistí a napravuje pokazené formáty meny z textu na čisté čísla
    def self_heal_amazon_amount(value):
        if pd.isna(value) or str(value).strip() == '':
            return None
            
        # Odstránenie tisíckových čiarok, znakov meny a bielych znakov automaticky
        price_str = str(value).strip()
        if ',' in price_str and '.' in price_str:
            price_str = price_str.replace(',', '')
        elif ',' in price_str and '.' not in price_str:
            price_str = price_str.replace(',', '.')
            
        price_str = price_str.replace('$', '').replace('€', '').strip()
        
        try:
            return Decimal(price_str)
        except InvalidOperation:
            return None

    # Automaticky opravíme a pretransformujeme stĺpec s peniazmi
    df['Amount_Decimal_Obj'] = df['Amount'].apply(self_heal_amazon_amount)
    
    # Pre potreby Pandera validácie vytvoríme float verziu
    df['Amount_Decimal'] = df['Amount_Decimal_Obj'].apply(lambda x: float(x) if x is not None else None)
    df['Qty'] = pd.to_numeric(df['Qty'], errors='coerce').fillna(0).astype(int)

    print("🛡️ Running declarative data quality checks via Pandera schema evaluation...")
    validated_df = amazon_schema.validate(df)
    
    # Izolácia neopraviteľných záznamov do stavového riadku ( sibling column )
    validated_df['data_quality_status'] = validated_df['Amount_Decimal'].apply(lambda x: 'CLEAN' if x is not None else 'UNKNOWN')
    
    print("\n=== 🎉 DATA VALIDATION & CLEANSING COMPLETED SUCCESSFULLY ===")
    
    # Pokračujeme v bezpečnej finančnej analýze nad overenými dátami
    clean_numeric_df = validated_df[validated_df['data_quality_status'] == 'CLEAN']
    gross_revenue = sum(clean_numeric_df['Amount_Decimal_Obj'].dropna())
    print(f"Total Gross Revenue: {float(gross_revenue):,.2f} EUR")
    
    invalid_statuses = ['Cancelled', 'Shipped - Returned to Seller', 'Returned']
    clean_cashflow_df = clean_numeric_df[~clean_numeric_df['Status'].isin(invalid_statuses)]
    net_revenue = sum(clean_cashflow_df['Amount_Decimal_Obj'].dropna())
    print(f"Total Net Revenue (Clean): {float(net_revenue):,.2f} EUR")
    
    print("\n🏆 ANALYTICS RUN COMPLETED SUCCESSFULLY.")

except pa.errors.SchemaError as schema_fault:
    print(f"\n❌ DATA QUALITY BREACH DETECTED BY PANDERA:\n{schema_fault}", file=sys.stderr)
    sys.exit(1)
except Exception as e:
    print(f"\n❌ PIPELINE CRITICAL FAILURE: {e}", file=sys.stderr)
    sys.exit(1)
