# 📊 Amazon Sales & Revenue Performance Pipeline

An advanced end-to-end data analytics project that processes over **128,000 corporate transaction rows** from Amazon India. This project replaces raw, uncleaned figures with an automated pipeline to calculate true business profitability, filtering out over **₹8.1 Million in losses** from cancellations and returns.

## 🚀 Interactive Dashboard Preview
![Amazon Sales Dashboard](dashboard_preview.gif)

---

## 🎯 Executive Business Summary

By conducting exploratory data analysis (EDA) and engineering a custom database financial pipeline, the following critical business insights were uncovered for the merchant:

1. **The Revenue Gap:** Total Gross Revenue was **₹78,592,678.30**. However, due to high cancellation and return rates, the actual **Net Revenue (Clean)** is **₹70,403,750.00**. The business was tracking **₹8,188,928.30 in lost revenue** without knowing the exact product triggers.
2. **The Product King:** The product category **"Set"** is the absolute bestseller, driving **50,284 successful orders** and generating **₹35,100,949** in clean net revenue.
3. **The Size Sweet Spot:** Size **"M"** dominates across all product lines, generating the highest profit margins, indicating where the merchant should optimize inventory stock.
4. **Seasonal Peak:** **April 2022 (Month 04)** experienced the highest revenue spike, identifying the business's peak commercial season.

---

## 🛠️ Tech Stack & Engineering Architecture

- **Data Engineering:** Python (Pandas) for data cleansing, outlier handling, and structural transformations.
- **Database Architecture:** PostgreSQL (psycopg2 & SQLAlchemy) chunks for high-speed massive dataset storage.
- **Business Logic:** Advanced SQL Views (`CASE WHEN` queries) to dynamically compute financial metrics.
- **BI Visualization:** Power BI Desktop tailored with an executive Indian Rupee (`₹`) international formatting system.

---

## 🔧 How the Pipeline Works

### 1. Python Data Cleansing (`clean_ecommerce.py`)
- Automatically flags high-volume missing data.
- Standardizes financial types, handles currency parsing, and maps raw e-commerce categorical fields.

### 2. SQL Views Integration (`upload_to_sql.py`)
- Isolates cancelled and returned orders dynamically using a permanent database layer:
```sql
CREATE VIEW public.v_amazon_net_financials AS
SELECT 
    "Order ID" AS order_id,
    TO_DATE("Date", 'MM-DD-YY') AS order_date,
    CASE 
        WHEN "Status" IN ('Cancelled', 'Shipped - Returned to Seller', 'Returned') THEN 0
        ELSE "Amount"
    END AS net_amount
FROM public.amazon_sales_raw;
```

---

## 💼 Business Impact & Deliverables
This automated solution saves the operations team approximately **5–8 hours per week** of manual Excel sheets aggregation, providing the CEO with a single, real-time source of truth for manufacturing, logistics, and scaling decisions.
