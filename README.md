# 🏦 Banking Customer Intelligence Dashboard

A colourful, interactive website built with **Python, Streamlit, Pandas, Plotly and SQL**. Upload different CSV/Excel datasets and explore customer segments, transaction behaviour, banking trends, data quality and downloadable extracts.

## Features
- CSV, XLS and XLSX upload
- Automatic column detection plus manual column mapping for different dataset schemas
- KPI cards: transactions, unique customers, total value and average transaction
- Customer-level transaction frequency and value-based segments
- Monthly trends, segment distribution, location and payment-channel analysis
- Filters for city, segment, transaction type and date
- Data quality report: missing values, types and unique values
- Export filtered rows and KPI summary as CSV
- Synthetic sample banking dataset included

## Run on Windows PowerShell
```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt
py -m streamlit run app.py
```
If activation is blocked:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.venv\Scripts\Activate.ps1
```

## Deploy
Push the project to GitHub, then open https://share.streamlit.io/, sign in with GitHub, create an app, select your repository and `main` branch, set main file path to `app.py`, and deploy.

## Dataset columns
Recommended fields: customer ID, transaction date, amount, transaction type/channel, account type/segment, city/region and status. Not all are required. After uploading, expand **Configure / map your dataset columns** and select the matching fields.

## SQL and Power BI
Starter SQL queries are in `sql/banking_analysis.sql`. Import your dataset or exported CSV into Power BI and create cards, monthly line charts, segment donuts and channel/location bar charts.

Example DAX (rename table/columns to match your model):
```DAX
Total Transaction Value = SUM(Banking[Amount])
Total Transactions = COUNTROWS(Banking)
Unique Customers = DISTINCTCOUNT(Banking[Customer_ID])
Average Transaction = AVERAGE(Banking[Amount])
```

**Privacy:** Use synthetic, anonymised or properly authorised data only. Never upload account/card numbers, PINs, passwords, Aadhaar/PAN details or other sensitive financial information. This is an educational portfolio project, not a banking decision or fraud-detection system.
