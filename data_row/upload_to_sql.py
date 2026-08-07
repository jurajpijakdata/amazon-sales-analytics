import pandas as pd
from sqlalchemy import create_engine

file_path = 'data_row/amazon_sales.csv'
db_url = 'postgresql+psycopg2://postgres:postgres01@localhost:5432/postgres'

try:
    print("1. Loading dataset into Python...")
    df = pd.read_csv(file_path, low_memory=False)
    
    # Quick clean before database upload
    df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0)
    df['Qty'] = pd.to_numeric(df['Qty'], errors='coerce').fillna(0).astype(int)
    
    print("2. Connecting to PostgreSQL database...")
    engine = create_engine(db_url)
    
    print("3. Uploading 128k rows to 'amazon_sales_raw' table. Please wait...")
    # chunksize helps process large datasets smoothly
    df.to_sql('amazon_sales_raw', engine, schema='public', if_exists='replace', index=False, chunksize=10000)
    
    print("\n=== 🎉 SUCCESS! ALL DATA UPLOADED TO POSTGRESQL ===")

except Exception as e:
    print(f"\nDatabase Error: {e}")
