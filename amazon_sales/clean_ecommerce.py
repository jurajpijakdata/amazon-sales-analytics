import pandas as pd

file_path = 'data_row/amazon_sales.csv'

try:
    df = pd.read_csv(file_path, low_memory=False)
    
    # 1. Clean the Amount column
    df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0)
    
    # 2. Let's see the unique values in the Status column first to know what we have
    print("=== UNIQUE ORDER STATUSES IN DATASET ===")
    print(df['Status'].unique())
    
    print("\n=== GROSS VS NET REVENUE ANALYSIS ===")
    # Calculate Gross Revenue (everything including cancellations)
    gross_revenue = df['Amount'].sum()
    print(f"Total Gross Revenue: {gross_revenue:,.2f}")
    
    # Filter out cancelled and returned orders to get clean data
    # We keep only rows that are NOT Cancelled or Returned
    invalid_statuses = ['Cancelled', 'Shipped - Returned to Seller', 'Returned']
    clean_df = df[~df['Status'].isin(invalid_statuses)]
    
    # Calculate Net Revenue (clean money)
    net_revenue = clean_df['Amount'].sum()
    print(f"Total Net Revenue (Clean): {net_revenue:,.2f}")
    
    # Calculate money lost
    money_lost = gross_revenue - net_revenue
    print(f"Revenue Lost due to Cancellations/Returns: {money_lost:,.2f}")

except Exception as e:
    print(f"Error during analysis: {e}")
