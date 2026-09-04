# 📊 Amazon Sales & Revenue Performance Analytics Pipeline

A self-directed data engineering and business intelligence project demonstrating end-to-end data transformation, automated database modeling, and high-precision financial reporting. This project executes a robust Python and SQL pipeline over a large-scale e-commerce dataset containing **128,975 transactional records**, systematically uncovering **₹8.1 Million in hidden losses** due to cancellations and product returns.

## 🚀 Interactive Dashboard Preview
![Amazon Sales Dashboard](dashboard_preview.gif)

---

## 🔗 Dataset Provenance & Disclosure (Clone & Run Standard)
* **Data Source:** Publicly verified [Amazon Sale Report dataset via Kaggle](https://kaggle.com).
* **Scale:** 128,975 raw rows capturing transactions from Amazon India.
* **Testing Vibe:** This repository contains a lightweight **`Amazon_sales_sample.csv`** to ensure full reproducibility and execution checks for reviewers and target clients without requiring heavy local system storage or processing overhead.

---

## 🎯 Engineered Financial Insights
By deploying high-precision numeric types and strict data quality boundaries, this project systematically isolates transactional anomalies to calculate true commercial performance metrics across the Amazon India network:

1. **The Revenue Leakage:** Total Gross Revenue was calculated at **₹78,592,678.30**. By building strict status-filtering layers, the actual **Net Revenue (Clean)** was isolated at **₹70,403,750.00**, proving that **₹8,188,928.30 (10.4% of gross volume)** was tied up in logistics failures (cancellations and returns).
2. **The Product Leader:** The **"Set"** product category stands as the core revenue driver, registering **50,284 successful orders** and yielding **₹35,100,949** in sanitized net revenue.
3. **Inventory Sweet Spot:** Size **"M"** systematically dominates order velocity across all main product lines, establishing the highest high-volume transaction metrics.
4. **Commercial Peak:** Time-series sorting identifies **April 2022 (Month 04)** as the highest historical revenue spike.

---

## 🛠️ Tech Stack & Pipeline Architecture
- **Data Engineering:** Python (Pandas) executing high-precision numeric vectoring via `decimal.Decimal` to eliminate fractional binary float drifting (`://30000000000000004.com`). Loose zero-interpolation methods (`.fillna(0)`) have been entirely deprecated to protect the mathematical and accounting validity of gross and net metrics.
- **Data Quality Isolation (Regex Shield):** Implements an explicit character parsing grammar (`^-?\\d+(?:\\.\\d+)?$`) to intercept malformed alphanumeric payloads and formatting anomalies, isolating them cleanly into a detached metadata bucket (`data_quality_status = 'UNKNOWN'`).
- **Database Architecture:** PostgreSQL (SQLAlchemy + `psycopg2-binary`) deploying optimized bulk block write configurations (`chunksize=10000`) and secure Connection Pooler layers (Port `6543`).
- **BI Visualization:** Power BI Desktop configured with custom localization schemas for the Indian Rupee (`₹`) financial system, optimized for flawless metric aggregations (`SUM()` and `AVERAGE()`).

---

## 📁 Repository Structure
* `amazon_analytics.py`: Main financial calculation engine processing local data extractions, handling negative sign refund vectors, isolating clean cash flows, and validating gross vs. net revenue metrics.
* `amazon_ingestion.py`: Dual-Mode Relational Ingestion Blueprint. Runs out-of-the-box as an architectural proof-of-concept for target clients, while actively converting into an online cloud stream loader upon secure `.env` connection pooler target mapping.
* `.gitignore`: Built-in production hygiene shield blocking temporary systemic directories and private parameter environments from public disclosure.
* `requirements.txt`: Locked software dependency versions ensuring 100% reproducible execution parameters across external infrastructures.

---

## 🚀 Quick Start (Clone & Run Standard)

### 1. Replicate Local Dependencies
Deploy the isolated software version scheme inside your internal environment:
```powershell
pip install -r requirements.txt
```

### 2. Run the Local Financial Validation Audit
To verify the analytical layer using the pre-packaged sample data pool, execute:
```powershell
python amazon_analytics.py
```

### 3. Inspect the Ingestion Architecture Blueprint
Test the dual-mode framework pipeline to inspect database ingestion scalability configurations:
```powershell
python amazon_ingestion.py
```

---
*Engineered under the UpDataLogic Performance Framework for transparent, honest, and reproducible analytics pipelines.*
