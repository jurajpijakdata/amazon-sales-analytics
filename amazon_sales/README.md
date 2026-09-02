# 📊 Amazon Sales & Revenue Performance Analytics Pipeline

A self-directed data engineering and business intelligence project demonstrating end-to-end data transformation, automated database modeling, and financial reporting. This project executes a robust Python and SQL pipeline over a large-scale e-commerce dataset containing **128,975 transactional records**, uncovering **₹8.1 Million in hidden losses** due to cancellations and product returns.

## 🚀 Interactive Dashboard Preview
![Amazon Sales Dashboard](dashboard_preview.gif)

---

## 🔗 Dataset Provenance & Disclosure (Rule 5)
* **Data Source:** Publicly verified [Amazon Sale Report dataset via Kaggle](https://kaggle.com).
* **Scale:** 128,975 raw rows capturing transactions from Amazon India.
* **Testing Vibe:** This repository contains a lightweight **`Amazon_sales_sample.csv` (100 rows)** to ensure full reproducibility and execution checks for reviewers without requiring heavy local system storage.

---

## 🎯 Engineered Financial Insights
By developing an automated cleaning structure and relational database views, this project systematically isolates transactional anomalies to calculate true commercial performance metrics:

1. **The Revenue Leakage:** Total Gross Revenue was calculated at **₹78,592,678.30**. By building strict status-filtering rules, the actual **Net Revenue (Clean)** was isolated at **₹70,403,750.00**, proving that **₹8,188,928.30 (10.4% of gross volume)** was tied up in logistics failures (cancellations and returns).
2. **The Product Leader:** The **"Set"** product category stands as the core revenue driver, registering **50,284 successful orders** and yielding **₹35,100,949** in sanitized net revenue.
3. **Inventory Sweet Spot:** Size **"M"** systematically dominates order velocity across all main product lines, establishing the highest high-volume profit margins.
4. **Commercial Peak:** Time-series sorting identifies **April 2022 (Month 04)** as the highest historical revenue spike.

---

## 🛠️ Tech Stack & Pipeline Architecture
- **Data Engineering:** Python (Pandas) executing string trimming, date formatting, outlier suppression, and structural data sanitization.
- **Database Architecture:** PostgreSQL (SQLAlchemy + `psycopg2-binary`) deploying bulk stream loading configurations.
- **Semantic Layer:** Advanced SQL Views utilizing dynamic `CASE WHEN` logic to filter operational statuses at the database layer.
- **BI Visualization:** Power BI Desktop configured with custom localization schemas for the Indian Rupee (`₹`) financial system.

---

## 🔧 Operational Walkthrough

### 1. Data Cleaning Stage (`amazon_analytics.py`)
Standardizes missing indices, suppresses structural white spaces in categorical variables, and reformats currency columns to ensure numerical stability.

### 2. Database Analytical Layer (`amazon_database_load.py`)
Isolates cancelled and returned orders dynamically at the core storage layer using a permanent automated SQL view:
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

## 🚀 Quick Start (Clone & Run Standard)

### 1. Replicate Local Dependencies
Deploy the isolated software version scheme:
```powershell
pip install -r requirements.txt
```

### 2. Run the Operational Analytics
To verify the analytical layer using the pre-packaged 100-row sample data pool, execute:
```powershell
python amazon_sales/amazon_analytics.py
```

---
*Engineered under the UpDataLogic Performance Framework for transparent, honest, and reproducible analytics pipelines.*
