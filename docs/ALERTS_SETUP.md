# 🔔 Real-Time Alerts & Notifications - Complete Guide

Comprehensive guide to the intelligent alert system for proactive vendor monitoring.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Alert Types](#alert-types)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Email Setup](#email-setup)
- [Dashboard](#dashboard)
- [Automation](#automation)
- [Customization](#customization)
- [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

The alert system monitors your vendor data 24/7 and notifies you of critical issues before they impact your business. It transforms reactive problem-solving into proactive management.

### Business Value
- ⚡ **Prevent stockouts** - Alert before inventory runs out
- 💰 **Stop losses** - Catch negative profit items immediately
- 📊 **Optimize capital** - Flag excess inventory automatically
- 🚨 **Early warning** - Detect issues before they escalate
- 📧 **Stay informed** - Email notifications to your inbox

---

## 🔔 Alert Types

### 1. Low Profit Margin 📉

**Trigger:** Profit margin < 15%

**Priority:** 🟠 HIGH

**Message:** 
```
Profit margin (12.5%) below threshold (15.0%)
```

**Recommendation:**
```
Review pricing strategy or negotiate better purchase terms
```

**When to act:** Within 1 week

---

### 2. Negative Profit 💸

**Trigger:** Gross profit < $0

**Priority:** 🔴 CRITICAL

**Message:**
```
NEGATIVE PROFIT: Losing $245.50
```

**Recommendation:**
```
URGENT: Review immediately - selling at a loss!
```

**When to act:** IMMEDIATELY

---

### 3. Low Stock Turnover 🐌

**Trigger:** Stock turnover < 0.3x

**Priority:** 🟡 MEDIUM

**Message:**
```
Slow-moving inventory (turnover: 0.2x)
```

**Recommendation:**
```
Consider discounting or promotional activities
```

**When to act:** Within 2 weeks

---

### 4. Overstocked Items 📦

**Trigger:** IsOverstocked = True (from inventory optimization)

**Priority:** 🟠 HIGH

**Message:**
```
Overstocked - excessive inventory value
```

**Recommendation:**
```
Reduce ordering, consider clearance sale
```

**When to act:** Within 1 week

---

### 5. Understocked Items ⚠️

**Trigger:** IsUnderstocked = True (from inventory optimization)

**Priority:** 🔴 CRITICAL

**Message:**
```
Stock level critically low
```

**Recommendation:**
```
URGENT: Reorder immediately to avoid stockout
```

**When to act:** IMMEDIATELY

---

### 6. Anomalous Behavior 🚨

**Trigger:** Anomaly score < -0.5

**Priority:** 🟡 MEDIUM

**Message:**
```
Unusual behavior pattern detected
```

**Recommendation:**
```
Investigate for data quality issues or exceptional circumstances
```

**When to act:** Within 1 week

---

### 7. Poor Performance ❌

**Trigger:** Performance score < 30/100

**Priority:** 🟠 HIGH

**Message:**
```
Poor overall performance score (25.3/100)
```

**Recommendation:**
```
Review vendor relationship - consider alternatives
```

**When to act:** Within 2 weeks

---

### 8. High Inventory Value 💰

**Trigger:** Total purchase dollars > $50,000

**Priority:** 🟢 LOW

**Message:**
```
High inventory value - monitor closely
```

**Recommendation:**
```
Track closely to ensure adequate return on investment
```

**When to act:** Monitor monthly

---

## 📦 Installation

### Prerequisites

Already installed if you completed basic setup:
```bash
pip install pandas sqlalchemy
# smtplib comes with Python (no install needed)
```

### Verify Installation

```bash
python -c "import smtplib; print('✅ Email library ready')"
```

---

## ⚙️ Configuration

### Basic Alert Thresholds

Edit `pipeline/alerts.py`, lines 30-46:

```python
class AlertConfig:
    # Alert thresholds - CUSTOMIZE THESE
    LOW_PROFIT_MARGIN = 15.0          # Alert if < 15%
    LOW_STOCK_TURNOVER = 0.3          # Alert if < 0.3x
    HIGH_INVENTORY_VALUE = 50000      # Alert if > $50K
    NEGATIVE_PROFIT = True            # Alert on negative profit
    ANOMALY_SCORE_THRESHOLD = -0.5    # Alert if < -0.5
    POOR_PERFORMANCE_SCORE = 30       # Alert if < 30/100
    
    # Priority levels (don't change)
    PRIORITY_CRITICAL = "🔴 CRITICAL"
    PRIORITY_HIGH = "🟠 HIGH"
    PRIORITY_MEDIUM = "🟡 MEDIUM"
    PRIORITY_LOW = "🟢 LOW"
```

### Example Customizations

**More strict profit threshold:**
```python
LOW_PROFIT_MARGIN = 20.0  # Alert at 20% instead of 15%
```

**Higher inventory value threshold:**
```python
HIGH_INVENTORY_VALUE = 100000  # $100K instead of $50K
```

**More anomaly sensitivity:**
```python
ANOMALY_SCORE_THRESHOLD = -0.3  # Catch more anomalies
```

---

## 📧 Email Setup

### Gmail Configuration (Recommended)

Edit `pipeline/alerts.py`, lines 32-37:

```python
class AlertConfig:
    # Email settings
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587
    SENDER_EMAIL = "your-email@gmail.com"        # YOUR EMAIL
    SENDER_PASSWORD = "your-app-password"         # APP PASSWORD (not regular password!)
    RECIPIENT_EMAILS = ["boss@company.com", "team@company.com"]  # WHO GETS ALERTS
```

### Get Gmail App Password

**Step 1:** Enable 2-Factor Authentication
1. Go to [Google Account](https://myaccount.google.com/)
2. Security → 2-Step Verification
3. Turn it ON if not already

**Step 2:** Generate App Password
1. Security → App passwords
2. Select "Mail" and your device
3. Click "Generate"
4. Copy the 16-character password
5. Use this in `SENDER_PASSWORD` (no spaces)

**Step 3:** Test Configuration
```bash
cd pipeline
python alerts.py --test
```

Expected output:
```
📧 Testing email configuration...
✅ Email alert sent to boss@company.com
```

---

### Other Email Providers

**Outlook.com:**
```python
SMTP_SERVER = "smtp-mail.outlook.com"
SMTP_PORT = 587
```

**Yahoo Mail:**
```python
SMTP_SERVER = "smtp.mail.yahoo.com"
SMTP_PORT = 587
```

**Custom SMTP:**
```python
SMTP_SERVER = "mail.yourcompany.com"
SMTP_PORT = 587  # or 465 for SSL
```

---

## 🚀 Usage

### Generate Alerts (Console Only)

```bash
cd pipeline
python run.py
# Select option 7: Generate Alerts
```

Or directly:
```bash
python alerts.py
```

**Output:**
```
======================================================================
🔔 ALERT SUMMARY
======================================================================
Total Alerts: 47
🔴 Critical: 8
🟠 High: 15
🟡 Medium: 18
🟢 Low: 6
======================================================================

🔴 CRITICAL ALERTS (Action Required IMMEDIATELY):

1. Negative Profit
   Vendor: ABC Supply Co.
   Item: Product XYZ
   Issue: NEGATIVE PROFIT: Losing $245.50
   Action: URGENT: Review immediately - selling at a loss!

2. Understocked Item
   Vendor: Best Vendor Inc.
   Item: Popular Product
   Issue: Stock level critically low
   Action: URGENT: Reorder immediately to avoid stockout
   
... (more alerts)
```

---

### Generate & Send Email Alerts

```bash
python run.py
# Select option 8: Generate & Email Alerts
```

Or directly:
```bash
python alerts.py --email
```

**What happens:**
1. Generates all alerts
2. Saves to database
3. Prints summary to console
4. Sends HTML email to configured recipients

**Email will include:**
- Alert count summary
- Top 10 critical alerts (detailed)
- Top 10 high priority alerts (detailed)
- Action recommendations

---

### View Alert Dashboard

```bash
python run.py
# Select option 9: Launch Alert Dashboard
```

Or directly:
```bash
streamlit run dashboard_alerts.py
```

**Dashboard auto-refreshes every 60 seconds!**

---

## 📊 Alert Dashboard

### Features

#### Tab 1: Critical Alerts 🔴
- Shows all CRITICAL priority items
- Red highlighting
- Detailed information
- Action recommendations

#### Tab 2: High Priority 🟠
- Shows HIGH priority items
- Orange highlighting
- Requires attention soon

#### Tab 3: All Alerts 📊
- Searchable/filterable table
- All priorities
- Export to CSV option

#### Tab 4: Analytics 📈
- Pie chart: Alerts by priority
- Bar chart: Alerts by type
- Bar chart: Top vendors with issues

#### Tab 5: History 📜
- Historical alert trends
- Time-based filtering (1/7/30/90 days)
- Trend line charts
- Pattern identification

---

### Dashboard Actions

**Refresh Alerts:**
- Click "🔄 Refresh Alerts" button
- Or wait 60 seconds for auto-refresh

**Filter Alerts:**
- Tab 3: Use multi-select filters
- Filter by priority
- Filter by type

**Download Report:**
- Tab 3: Click "📥 Download Alert Report"
- Gets CSV of all filtered alerts

---

## ⏰ Automation

### Daily Alert Checks

**Windows Task Scheduler:**

1. Open Task Scheduler
2. Create Basic Task
3. Name: "Vendor Alerts"
4. Trigger: Daily at 8:00 AM
5. Action: Start a program
   - Program: `python`
   - Arguments: `C:\path\to\pipeline\alerts.py --email`
   - Start in: `C:\path\to\project`
6. Save

---

**Mac/Linux Cron:**

```bash
# Edit crontab
crontab -e

# Add line (runs daily at 8 AM)
0 8 * * * cd /path/to/project && python pipeline/alerts.py --email
```

---

### Weekly Alert Summary

```bash
# Every Monday at 9 AM
# Windows Task Scheduler: Set trigger to "Weekly, Monday, 9:00 AM"

# Cron:
0 9 * * 1 cd /path/to/project && python pipeline/alerts.py --email
```

---

### Real-Time Monitoring

Keep dashboard running:

```bash
# Start in background
streamlit run dashboard_alerts.py &

# Or use screen/tmux to keep running
screen -S alerts
streamlit run dashboard_alerts.py
# Press Ctrl+A, then D to detach
```

---

## 🎨 Customization

### Add Custom Alert Type

**Step 1:** Add to AlertType class (line ~60):

```python
class AlertType:
    # Existing types...
    CUSTOM_ALERT = "My Custom Alert"
```

**Step 2:** Create check function:

```python
def check_custom_alerts(df):
    alerts = []
    
    # Your logic here
    problem_items = df[df['YourCondition'] == True]
    
    for _, row in problem_items.iterrows():
        alerts.append({
            'type': AlertType.CUSTOM_ALERT,
            'priority': AlertConfig.PRIORITY_HIGH,
            'vendor': row['VendorName'],
            'description': row['Description'],
            'metric_value': f"{row['YourMetric']:.2f}",
            'threshold': "Your threshold",
            'message': "Your custom message",
            'recommendation': "Your recommendation"
        })
    
    return alerts
```

**Step 3:** Add to generate_all_alerts (line ~400):

```python
def generate_all_alerts():
    # ... existing code ...
    
    # Add your custom check
    all_alerts.extend(check_custom_alerts(df))
    
    return all_alerts
```

---

### Customize Email Template

Edit `alerts.py`, line ~300:

```python
html_content = f"""
<html>
<head>
    <style>
        /* Your custom CSS here */
        body {{ font-family: Arial, sans-serif; }}
        .custom-class {{ color: red; }}
    </style>
</head>
<body>
    <!-- Your custom HTML here -->
    <h1>Custom Alert Email</h1>
    <!-- ... -->
</body>
</html>
"""
```

---

### Change Alert Priorities

Edit the check functions to assign different priorities:

```python
def check_profit_alerts(df):
    # ...
    alerts.append({
        'priority': AlertConfig.PRIORITY_CRITICAL,  # Change to MEDIUM
        # ...
    })
```

---

## 📊 Understanding Alert Logic

### When Alerts are Generated

Alerts are checked against **current data** in:
- `vendor_sales_summary` (required)
- `vendor_performance_scores` (optional, from analytics)
- `inventory_recommendations` (optional, from analytics)
- `vendor_anomalies` (optional, from analytics)

**If analytics tables don't exist:**
- Only profit and inventory alerts work
- Performance and anomaly alerts are skipped
- Run analytics first for full alert coverage

---

### Alert Lifecycle

```
1. Data updated (pipeline runs)
        ↓
2. Analytics runs (optional but recommended)
        ↓
3. Alerts generated (check all conditions)
        ↓
4. Alerts saved to database
   - active_alerts (current)
   - alert_history (all time)
        ↓
5. Display in dashboard / Send email
        ↓
6. Take action on alerts
        ↓
7. Next cycle (repeat)
```

---

### Alert Deduplication

**Current behavior:**
- `active_alerts` table is **replaced** each run
- Only current issues shown
- Old alerts automatically cleared

**History tracking:**
- `alert_history` table **appends** all alerts
- Never deleted
- Used for trend analysis

---

## 🐛 Troubleshooting

### Issue: "Email not sending"

**Symptom:**
```
❌ Failed to send email: Authentication failed
```

**Solutions:**

**1. Verify credentials:**
```python
# Check in alerts.py
print(AlertConfig.SENDER_EMAIL)
print(len(AlertConfig.SENDER_PASSWORD))  # Should be 16 chars
```

**2. Use app password, not regular password:**
- Gmail requires app-specific password
- See Email Setup section above

**3. Check 2FA is enabled:**
- Required for Gmail app passwords

**4. Test with simple script:**
```python
import smtplib
from email.mime.text import MIMEText

msg = MIMEText("Test")
msg['Subject'] = 'Test'
msg['From'] = 'your-email@gmail.com'
msg['To'] = 'recipient@example.com'

with smtplib.SMTP('smtp.gmail.com', 587) as server:
    server.starttls()
    server.login('your-email@gmail.com', 'app-password')
    server.send_message(msg)
```

---

### Issue: "No alerts generated"

**Symptom:**
```
✅ No alerts - all systems normal!
```

**If this seems wrong:**

**1. Check thresholds:**
```python
# Maybe thresholds are too strict/loose
AlertConfig.LOW_PROFIT_MARGIN = 15.0  # Lower to generate more alerts
```

**2. Verify data exists:**
```python
import pandas as pd
from sqlalchemy import create_engine

engine = create_engine('sqlite:///inventory.db')
df = pd.read_sql("SELECT MIN(ProfitMargin), MAX(ProfitMargin) FROM vendor_sales_summary", engine)
print(df)  # Check if any values are below threshold
```

**3. Run analytics first:**
```bash
# Some alerts need analytics data
python analytics.py
python alerts.py
```

---

### Issue: "Dashboard shows no alerts"

**Symptom:**
Dashboard says "No Active Alerts" but alerts were generated

**Solutions:**

**1. Check if table exists:**
```python
import pandas as pd
from sqlalchemy import create_engine

engine = create_engine('sqlite:///inventory.db')
tables = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table'", engine)
print(tables)  # Should include active_alerts
```

**2. Check table has data:**
```python
df = pd.read_sql("SELECT COUNT(*) FROM active_alerts", engine)
print(df)  # Should be > 0
```

**3. Refresh dashboard:**
- Click "🔄 Refresh Alerts" button
- Or press 'R' key in browser

---

### Issue: "Too many alerts"

**Symptom:**
Getting 500+ alerts, overwhelming

**Solutions:**

**1. Adjust thresholds to be less sensitive:**
```python
AlertConfig.LOW_PROFIT_MARGIN = 10.0   # Lower threshold
AlertConfig.LOW_STOCK_TURNOVER = 0.2   # Lower threshold
```

**2. Focus on critical/high only:**
- Filter dashboard to show only top priorities
- Email only critical alerts

**3. Review data quality:**
- Too many alerts might indicate data issues
- Check for duplicates or errors

---

### Issue: "Email sent but not received"

**Solutions:**

**1. Check spam folder:**
- Automated emails often go to spam
- Add sender to contacts

**2. Verify recipient email:**
```python
print(AlertConfig.RECIPIENT_EMAILS)
# Make sure email is correct
```

**3. Check email provider limits:**
- Some providers limit bulk emails
- Gmail: 500/day limit

---

## 📈 Best Practices

### 1. Run Alerts After Analytics

```bash
# Optimal workflow
python pipeline.py --archive    # Step 1: Load data
python analytics.py             # Step 2: ML analysis
python alerts.py --email        # Step 3: Check & notify
```

### 2. Check Alerts Daily

- Set up daily automated check
- Review dashboard each morning
- Act on critical alerts immediately

### 3. Tune Thresholds Over Time

- Start conservative
- Adjust based on false positives
- Seasonal adjustments

### 4. Act on Alerts Promptly

- Critical: Same day
- High: Within 1 week
- Medium: Within 2 weeks
- Low: Monitor monthly

### 5. Track Alert Trends

- Use history tab in dashboard
- Identify recurring issues
- Address root causes

---

## 💡 Use Cases

### Morning Routine

```bash
# 1. Check for new alerts
cd pipeline
python alerts.py

# 2. Review dashboard
python run.py → option 9

# 3. Take action on critical items
# 4. Email team summary if needed
python alerts.py --email
```

---

### Weekly Review

```bash
# 1. Generate weekly alert summary
python alerts.py --email

# 2. Review alert history
# In dashboard: Tab 5, select "Last 7 days"

# 3. Identify patterns
# Which vendors trigger most alerts?
# What types of alerts are most common?

# 4. Adjust processes
# Fix root causes
# Update thresholds if needed
```

---

## 🎯 Summary

**Alert System Features:**
- ✅ 8 intelligent alert types
- ✅ 4 priority levels
- ✅ Email notifications (HTML formatted)
- ✅ Interactive dashboard
- ✅ Alert history tracking
- ✅ Customizable thresholds
- ✅ Automated scheduling

**Typical Results:**
- Alerts generated: 50-200 per run
- Critical alerts: 5-20 (immediate action)
- Processing time: 30-60 seconds
- Email delivery: < 5 seconds

**Prerequisites:**
- Pipeline must run first (loads data)
- Analytics recommended (more alert types)
- Email optional (works without)

---

## 🆘 Getting Help

If issues persist:

1. **Check logs**: `logs/alerts.log`
2. **Verify email config**: Run `python alerts.py --test`
3. **Check database**: Ensure tables exist
4. **Open issue**: Include error message and config

---

**Never miss a critical issue again!** 🔔
