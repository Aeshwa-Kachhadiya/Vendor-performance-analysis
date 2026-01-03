# 🚀 Setup Guide

Complete installation and configuration guide for the AI-Powered Vendor Analytics Platform.

---

## 📋 Prerequisites

### System Requirements
- **Python**: 3.11 or higher
- **RAM**: 4GB minimum (8GB recommended for large datasets)
- **Storage**: 500MB for application + data storage
- **OS**: Windows, macOS, or Linux

### Check Python Version
```bash
python --version
# Should show: Python 3.11.x or higher
```

If you don't have Python 3.11+:
- **Windows/Mac**: Download from [python.org](https://www.python.org/downloads/)
- **Linux**: `sudo apt-get install python3.11`

---

## 📦 Installation

### Step 1: Clone the Repository
```bash
git clone https://github.com/yourusername/vendor-analytics.git
cd vendor-analytics
```

### Step 2: Create Virtual Environment (Recommended)
```bash
# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate

# Mac/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

**What gets installed:**
```txt
streamlit>=1.28.0          # Interactive dashboards
pandas>=2.0.0              # Data manipulation
numpy>=1.24.0              # Numerical computing
openpyxl>=3.1.0            # Excel file handling
sqlalchemy>=2.0.0          # Database ORM
plotly>=5.18.0             # Interactive visualizations
scipy>=1.11.0              # Statistical functions
scikit-learn>=1.3.0        # Machine learning
schedule                   # Task scheduling
watchdog                   # File system monitoring
```

### Step 4: Verify Installation
```bash
# Test if all packages installed correctly
python -c "import streamlit, pandas, sklearn; print('✅ All packages installed!')"
```

---

## 📁 Project Structure Setup

### Create Required Folders
```bash
# Create folder structure
mkdir -p data/archive logs

# Your structure should look like:
# vendor-analytics/
# ├── pipeline/
# ├── data/
# │   └── archive/
# ├── logs/
# ├── dashboard.py
# └── ...
```

### Verify Structure
```bash
# Check if folders exist
ls -la
# Should see: pipeline/, data/, logs/
```

---

## 📊 Data Preparation

### Step 1: Prepare Your Excel Files

You need **two Excel files**:

**1. sales.xlsx** - Must have these columns:
- `VendorName` - Name of the vendor
- `Description` - Product description
- `SalesQuantity` - Number of units sold
- `SalesDollars` - Total sales amount

**2. purchases.xlsx** - Must have these columns:
- `VendorName` - Name of the vendor
- `Description` - Product description
- `Quantity` - Number of units purchased
- `Dollars` - Total purchase amount

### Step 2: Place Files in Data Folder
```bash
cp /path/to/your/sales.xlsx data/
cp /path/to/your/purchases.xlsx data/
```

### Step 3: Verify Data Format
```bash
# Quick check using Python
python -c "
import pandas as pd
sales = pd.read_excel('data/sales.xlsx')
print('Sales columns:', sales.columns.tolist())
purchases = pd.read_excel('data/purchases.xlsx')
print('Purchase columns:', purchases.columns.tolist())
"
```

---

## ⚙️ Configuration

### Basic Configuration (Optional)

Edit `pipeline/config.py` to customize settings:

```python
# Paths - usually don't need to change
DATA_FOLDER = BASE_DIR / 'data'
LOG_FOLDER = BASE_DIR / 'logs'
DB_PATH = BASE_DIR / 'inventory.db'

# Pipeline Settings - adjust as needed
PIPELINE_SCHEDULE_HOURS = 24  # Run every 24 hours
FILE_WATCH_COOLDOWN = 30      # Wait 30 sec before re-processing
```

### Email Configuration (Optional)

To enable email alerts, edit `pipeline/alerts.py`:

```python
class AlertConfig:
    # Email settings
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587
    SENDER_EMAIL = "your-email@gmail.com"
    SENDER_PASSWORD = "your-app-password"  # Gmail app password
    RECIPIENT_EMAILS = ["recipient@example.com"]
```

**Gmail App Password Setup:**
1. Go to [Google Account Settings](https://myaccount.google.com/)
2. Security → 2-Step Verification (enable if not already)
3. Security → App passwords
4. Generate password for "Mail"
5. Use this password (not your regular Gmail password)

---

## 🧪 Test Your Installation

### Test 1: Run Pipeline Once
```bash
cd pipeline
python pipeline.py --archive
```

**Expected output:**
```
======================================================================
🚀 PIPELINE STARTED: 2024-01-15 10:30:00
======================================================================
📁 Found 2 Excel files
✅ Ingested sales: 10000 rows, 14 cols
✅ Ingested purchases: 8000 rows, 16 cols
✅ Data validation passed
✅ Vendor summary table created successfully
======================================================================
✅ PIPELINE COMPLETED: 0.5 minutes
======================================================================
```

### Test 2: Run Analytics
```bash
python analytics.py
```

**Expected output:**
```
🤖 ANALYTICS PIPELINE STARTED
✅ Loaded 500 vendor records
🎯 Step 1: Calculating vendor performance scores...
✅ Calculated performance scores for 500 vendors
📦 Step 2: Optimizing inventory levels...
✅ Generated inventory recommendations
...
```

### Test 3: Launch Dashboard
```bash
streamlit run ../dashboard.py
```

**Expected result:**
- Browser opens automatically
- Dashboard loads with your data
- No error messages

---

## 🚀 First Run Workflow

### Complete Setup Process
```bash
# 1. Navigate to pipeline folder
cd pipeline

# 2. Run the interactive menu
python run.py

# 3. Select option 13 (Quick Start)
# This will:
#   - Load your data
#   - Run ML analytics
#   - Generate alerts
#   - Launch dashboard
```

---

## 🐛 Troubleshooting

### Problem: "Module not found" error
**Solution:**
```bash
# Make sure virtual environment is activated
# Then reinstall dependencies
pip install -r requirements.txt
```

### Problem: "Excel file not found"
**Solution:**
```bash
# Check files are in correct location
ls data/
# Should show: sales.xlsx, purchases.xlsx

# Check file names match exactly
# Must be lowercase: sales.xlsx, purchases.xlsx
```

### Problem: "Column not found" error
**Solution:**
Your Excel files must have the exact column names. Check the Data Preparation section above.

### Problem: Database locked error
**Solution:**
```bash
# Close any programs accessing inventory.db
# Delete the database and rerun pipeline
rm inventory.db
python pipeline/pipeline.py --archive
```

### Problem: Streamlit won't start
**Solution:**
```bash
# Check if port 8501 is available
# Or specify different port
streamlit run dashboard.py --server.port 8502
```

### Problem: Email alerts not sending
**Solution:**
1. Verify email settings in `pipeline/alerts.py`
2. Use Gmail app password (not regular password)
3. Test with: `python alerts.py --test`

---

## 📊 Sample Data (For Testing)

If you don't have data yet, create sample files:

### Create sample sales.xlsx
```python
import pandas as pd

sample_sales = pd.DataFrame({
    'VendorName': ['Vendor A', 'Vendor B', 'Vendor A'] * 100,
    'Description': ['Product 1', 'Product 2', 'Product 3'] * 100,
    'SalesQuantity': [10, 15, 20] * 100,
    'SalesDollars': [100, 150, 200] * 100
})

sample_sales.to_excel('data/sales.xlsx', index=False)
print("✅ Created sample sales.xlsx")
```

### Create sample purchases.xlsx
```python
sample_purchases = pd.DataFrame({
    'VendorName': ['Vendor A', 'Vendor B', 'Vendor A'] * 100,
    'Description': ['Product 1', 'Product 2', 'Product 3'] * 100,
    'Quantity': [12, 18, 22] * 100,
    'Dollars': [60, 90, 120] * 100
})

sample_purchases.to_excel('data/purchases.xlsx', index=False)
print("✅ Created sample purchases.xlsx")
```

Run both scripts:
```bash
python create_sample_data.py
```

---

## ✅ Verification Checklist

Before considering setup complete:

- [ ] Python 3.11+ installed
- [ ] All dependencies installed (`pip list` shows all packages)
- [ ] Folder structure created (data/, logs/, pipeline/)
- [ ] Excel files placed in data/ folder with correct columns
- [ ] Pipeline runs successfully (option 1 in menu)
- [ ] Database created (inventory.db exists)
- [ ] Analytics runs successfully (option 4 in menu)
- [ ] Dashboard launches (option 10 or 11 in menu)
- [ ] Email configured (optional, test with option 8)

---

## 📚 Next Steps

After successful setup:

1. **Run the Quick Start**: `python run.py` → Option 13
2. **Explore Dashboards**: Try options 10, 11
3. **Set Up Alerts**: Configure email in `alerts.py`
4. **Automate Pipeline**: Set up scheduled runs
5. **Read Other Guides**: 
   - [Pipeline Guide](PIPELINE_README.md)
   - [Analytics Guide](ANALYTICS_SETUP.md)
   - [Alert Guide](ALERTS_SETUP.md)

---

## 🆘 Getting Help

If you encounter issues:

1. **Check logs**: Look in `logs/` folder
2. **Review error messages**: Read carefully
3. **Search issues**: Check GitHub issues
4. **Ask for help**: Open a new issue with:
   - Error message
   - Steps to reproduce
   - Your Python version
   - Operating system

---

## 🎉 You're Ready!

Setup complete! Your vendor analytics platform is ready to use.

**Quick command to get started:**
```bash
cd pipeline && python run.py
```

Happy analyzing! 🚀
