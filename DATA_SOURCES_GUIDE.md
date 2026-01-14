# TreasuryIQ Data Sources Guide

## 📊 **Complete Guide to Financial Data Sources for Treasury Management**

### **Overview**
This guide provides step-by-step instructions for accessing and integrating financial datasets into your TreasuryIQ platform for the Tableau Hackathon.

---

## **1. Government & Official Data Sources (Free)**

### **🏛️ US Treasury Department - Fiscal Data**
- **Website:** https://fiscaldata.treasury.gov/
- **API Documentation:** https://fiscaldata.treasury.gov/api-documentation/
- **No API Key Required** ✅

#### **Key Datasets Available:**
1. **Daily Treasury Statement (DTS)**
   - Operating cash balances
   - Daily receipts and outlays
   - Public debt transactions
   - **API Endpoint:** `/accounting/dts/operating_cash_balance`

2. **Debt to the Penny**
   - Total public debt outstanding
   - Daily debt figures
   - **API Endpoint:** `/accounting/od/debt_to_penny`

3. **Interest Rate Statistics**
   - Treasury security rates
   - Average interest rates on debt
   - **API Endpoint:** `/accounting/od/avg_interest_rates`

#### **Sample API Call:**
```bash
curl "https://api.fiscaldata.treasury.gov/services/api/v1/accounting/dts/operating_cash_balance?filter=record_date:gte:2024-01-01&sort=-record_date"
```

### **🏦 Federal Reserve Economic Data (FRED)**
- **Website:** https://fred.stlouisfed.org/
- **API Documentation:** https://fred.stlouisfed.org/docs/api/fred/
- **API Key:** Free registration required

#### **Key Data Series:**
- **Treasury Rates:** GS3M, GS6M, GS1, GS2, GS5, GS10, GS30
- **Fed Funds Rate:** FEDFUNDS
- **Economic Indicators:** GDP, CPIAUCSL (inflation), UNRATE (unemployment)
- **Exchange Rates:** DEXUSEU (USD/EUR), DEXUSUK (USD/GBP)

#### **Registration Steps:**
1. Go to https://fred.stlouisfed.org/docs/api/api_key.html
2. Create free account
3. Request API key
4. Add to your `.env` file: `FEDERAL_RESERVE_API_KEY=your_key_here`

---

## **2. Market Data Sources**

### **📈 Alpha Vantage (Free Tier)**
- **Website:** https://www.alphavantage.co/
- **Free Tier:** 5 API requests per minute, 500 per day
- **API Key:** Free registration required

#### **Available Data:**
- Stock prices and fundamentals
- Forex rates (real-time and historical)
- Commodities (gold, oil, etc.)
- Economic indicators
- Treasury yield curves

#### **Registration Steps:**
1. Go to https://www.alphavantage.co/support/#api-key
2. Enter email to get free API key
3. Add to `.env`: `ALPHA_VANTAGE_API_KEY=your_key_here`

### **💹 Yahoo Finance (Free)**
- **Python Library:** `yfinance`
- **No API Key Required** ✅
- **Installation:** `pip install yfinance`

#### **Available Data:**
- Stock prices and indices
- Currency exchange rates
- Treasury ETF prices (as proxy for rates)
- Commodity prices

#### **Sample Usage:**
```python
import yfinance as yf

# Get Treasury 10-year yield
treasury_10y = yf.Ticker("^TNX")
current_yield = treasury_10y.history(period="1d")['Close'].iloc[-1]

# Get USD/EUR exchange rate
usd_eur = yf.Ticker("USDEUR=X")
fx_rate = usd_eur.history(period="1d")['Close'].iloc[-1]
```

---

## **3. Tableau Sample Datasets**

### **🏪 Built-in Tableau Datasets**
When you install Tableau Desktop, these datasets are included:

1. **Sample - Superstore**
   - Retail sales data
   - Can be adapted for treasury analysis
   - Location: Tableau installation folder

2. **World Indicators**
   - Economic data by country
   - GDP, population, life expectancy
   - Good for global treasury operations

3. **Sample - Financial**
   - Basic financial metrics
   - Revenue, profit, expenses by segment

### **🌐 Tableau Public Sample Data**
- **Website:** https://public.tableau.com/app/resources/sample-data
- **Datasets Include:**
  - Global economic indicators
  - Financial performance data
  - Regional sales data
  - Time series datasets

---

## **4. Implementation Steps**

### **Step 1: Set Up Environment Variables**
Create or update your `.env` file:

```bash
# Treasury Data APIs
FEDERAL_RESERVE_API_KEY=your_fred_api_key
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key
EXCHANGE_RATES_API_KEY=your_exchange_rates_key

# Demo Configuration
DEMO_MODE=true
DEMO_COMPANY_NAME=GlobalTech Industries
DEMO_TREASURY_SIZE=500000000
```

### **Step 2: Install Required Python Packages**
```bash
pip install yfinance pandas numpy aiohttp requests python-dotenv
```

### **Step 3: Test Data Sources**
Use our built-in API endpoints:

```bash
# Test sample data (no API keys required)
curl http://localhost:8000/api/v1/data-sources/demo/sample-data

# Test real data sources (requires API keys)
curl http://localhost:8000/api/v1/data-sources/market/interest-rates
curl http://localhost:8000/api/v1/data-sources/market/exchange-rates
curl http://localhost:8000/api/v1/data-sources/treasury/cash-balances
```

### **Step 4: Integrate with Tableau**
1. **Connect to API Data:**
   - Use Tableau's Web Data Connector
   - Point to your local API endpoints
   - Example: `http://localhost:8000/api/v1/data-sources/demo/sample-data`

2. **Use CSV Export:**
   - Export data from API to CSV
   - Import CSV into Tableau
   - Set up automatic refresh

---

## **5. Data Source Priority & Fallbacks**

### **Recommended Approach:**
1. **Primary:** Government sources (Treasury.gov, FRED) - Most reliable
2. **Secondary:** Alpha Vantage - Good coverage, rate limited
3. **Fallback:** Yahoo Finance - Free, unlimited, less reliable
4. **Demo:** Sample data - Always available for presentations

### **Error Handling:**
Our data service automatically falls back through sources:
```
Treasury.gov → FRED → Alpha Vantage → Yahoo Finance → Sample Data
```

---

## **6. Tableau Hackathon Specific Datasets**

### **For Treasury Management Use Case:**
1. **Cash Flow Data:**
   - Daily treasury balances
   - Cash receipts and outlays
   - Liquidity metrics

2. **Risk Data:**
   - Interest rate curves
   - Currency exchange rates
   - Credit spreads
   - Volatility indices

3. **Economic Context:**
   - GDP growth rates
   - Inflation indicators
   - Employment data
   - Central bank rates

### **Sample Data Structure:**
```json
{
  "treasury_balances": {
    "operating_cash_balance": 450000000000,
    "treasury_general_account": 420000000000,
    "federal_reserve_account": 30000000000
  },
  "interest_rates": {
    "treasury_3m": 5.25,
    "treasury_2y": 4.95,
    "treasury_10y": 4.65,
    "fed_funds": 5.50
  },
  "exchange_rates": {
    "EUR": 0.92,
    "GBP": 0.79,
    "JPY": 148.50
  }
}
```

---

## **7. Quick Start Commands**

### **Get API Keys (5 minutes):**
```bash
# 1. FRED API Key
open https://fred.stlouisfed.org/docs/api/api_key.html

# 2. Alpha Vantage API Key  
open https://www.alphavantage.co/support/#api-key

# 3. Update .env file with your keys
```

### **Test Data Integration (2 minutes):**
```bash
# Start your TreasuryIQ servers
cd backend && python demo_server.py &
cd frontend && npm run dev &

# Test data endpoints
curl http://localhost:8000/api/v1/data-sources/demo/sample-data
curl http://localhost:8000/api/v1/treasury/overview
```

### **Connect to Tableau (3 minutes):**
1. Open Tableau Desktop
2. Connect to Web Data Connector
3. Enter URL: `http://localhost:8000/api/v1/data-sources/demo/sample-data`
4. Load data and create visualizations

---

## **8. Troubleshooting**

### **Common Issues:**
1. **API Rate Limits:** Use demo data or implement caching
2. **CORS Errors:** Ensure CORS is enabled in backend
3. **Missing API Keys:** Use Yahoo Finance fallback
4. **Network Issues:** Use cached/sample data

### **Debug Commands:**
```bash
# Check data source status
curl http://localhost:8000/api/v1/data-sources/sources/status

# Test individual sources
curl http://localhost:8000/api/v1/data-sources/market/comprehensive

# View logs
tail -f backend/logs/treasuryiq.log
```

---

## **9. Next Steps**

1. **✅ Set up API keys** (optional, demo works without them)
2. **✅ Test data endpoints** using curl or browser
3. **✅ Connect Tableau** to your local API
4. **✅ Create visualizations** using the treasury data
5. **✅ Build interactive dashboards** for the hackathon

**Your TreasuryIQ platform is now ready with comprehensive financial data integration!**

---

## **Support**

- **Demo Data:** Always available at `/api/v1/data-sources/demo/sample-data`
- **API Documentation:** http://localhost:8000/docs
- **Sample Tableau Workbooks:** Available in `/tableau-samples/` directory

**Ready to build amazing treasury analytics with Tableau! 🚀**