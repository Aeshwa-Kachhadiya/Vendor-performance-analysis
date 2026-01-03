"""
Real-Time Alert System
Monitors vendor performance and sends notifications
"""

import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
from pathlib import Path
import logging
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json

# Setup
BASE_DIR = Path(__file__).parent.parent
DB_PATH = BASE_DIR / 'inventory.db'
engine = create_engine(f"sqlite:///{DB_PATH}")

log_dir = BASE_DIR / 'logs'
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / 'alerts.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# ================== ALERT CONFIGURATION ==================
class AlertConfig:
    """Alert thresholds and settings"""
    
    # Email settings (configure these)
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587
    SENDER_EMAIL = "your-email@gmail.com"  # Configure this
    SENDER_PASSWORD = "your-app-password"  # Configure this (use app password, not real password)
    RECIPIENT_EMAILS = ["recipient@example.com"]  # Configure this
    
    # Alert thresholds
    LOW_PROFIT_MARGIN = 15.0  # Alert if profit margin < 15%
    LOW_STOCK_TURNOVER = 0.3  # Alert if turnover < 0.3
    HIGH_INVENTORY_VALUE = 50000  # Alert if inventory value > $50k
    NEGATIVE_PROFIT = True  # Alert on negative profits
    ANOMALY_SCORE_THRESHOLD = -0.5  # Alert if anomaly score < -0.5
    
    # Performance thresholds
    POOR_PERFORMANCE_SCORE = 30  # Alert if performance score < 30
    OVERSTOCKED_DAYS = 90  # Alert if stock > 90 days supply
    UNDERSTOCKED_THRESHOLD = 0.5  # Alert if below reorder point by this factor
    
    # Alert priorities
    PRIORITY_CRITICAL = "🔴 CRITICAL"
    PRIORITY_HIGH = "🟠 HIGH"
    PRIORITY_MEDIUM = "🟡 MEDIUM"
    PRIORITY_LOW = "🟢 LOW"

# ================== ALERT TYPES ==================
class AlertType:
    """Types of alerts"""
    LOW_PROFIT = "Low Profit Margin"
    NEGATIVE_PROFIT = "Negative Profit"
    LOW_TURNOVER = "Low Stock Turnover"
    OVERSTOCKED = "Overstocked Item"
    UNDERSTOCKED = "Understocked Item"
    ANOMALY = "Anomalous Behavior"
    POOR_PERFORMANCE = "Poor Performance Score"
    HIGH_INVENTORY = "High Inventory Value"

# ================== ALERT ENGINE ==================
def load_data_for_alerts():
    """Load necessary data for alert checking"""
    try:
        # Load vendor summary
        vendor_df = pd.read_sql("SELECT * FROM vendor_sales_summary", engine)
        
        # Load performance scores if available
        try:
            scores_df = pd.read_sql("SELECT * FROM vendor_performance_scores", engine)
            vendor_df = vendor_df.merge(scores_df[['VendorName', 'Description', 'PerformanceScore']], 
                                        on=['VendorName', 'Description'], how='left')
        except:
            logging.warning("⚠️ Performance scores not available")
        
        # Load inventory recommendations if available
        try:
            inv_df = pd.read_sql("SELECT * FROM inventory_recommendations", engine)
            vendor_df = vendor_df.merge(inv_df[['VendorName', 'Description', 'IsOverstocked', 'IsUnderstocked']], 
                                        on=['VendorName', 'Description'], how='left')
        except:
            logging.warning("⚠️ Inventory recommendations not available")
        
        # Load anomalies if available
        try:
            anomaly_df = pd.read_sql("SELECT * FROM vendor_anomalies", engine)
            vendor_df = vendor_df.merge(anomaly_df[['VendorName', 'Description', 'AnomalyScore']], 
                                       on=['VendorName', 'Description'], how='left')
        except:
            logging.warning("⚠️ Anomaly data not available")
        
        logging.info(f"✅ Loaded {len(vendor_df)} vendor records for alert checking")
        return vendor_df
        
    except Exception as e:
        logging.error(f"❌ Failed to load data: {str(e)}")
        return None

def check_profit_alerts(df):
    """Check for profit-related alerts"""
    alerts = []
    
    # Low profit margin
    low_profit = df[df['ProfitMargin'] < AlertConfig.LOW_PROFIT_MARGIN]
    for _, row in low_profit.iterrows():
        alerts.append({
            'type': AlertType.LOW_PROFIT,
            'priority': AlertConfig.PRIORITY_HIGH,
            'vendor': row['VendorName'],
            'description': row['Description'],
            'metric_value': f"{row['ProfitMargin']:.2f}%",
            'threshold': f"{AlertConfig.LOW_PROFIT_MARGIN}%",
            'message': f"Profit margin ({row['ProfitMargin']:.2f}%) below threshold ({AlertConfig.LOW_PROFIT_MARGIN}%)",
            'recommendation': "Review pricing strategy or negotiate better purchase terms"
        })
    
    # Negative profit
    if AlertConfig.NEGATIVE_PROFIT:
        negative_profit = df[df['GrossProfit'] < 0]
        for _, row in negative_profit.iterrows():
            alerts.append({
                'type': AlertType.NEGATIVE_PROFIT,
                'priority': AlertConfig.PRIORITY_CRITICAL,
                'vendor': row['VendorName'],
                'description': row['Description'],
                'metric_value': f"${row['GrossProfit']:.2f}",
                'threshold': "$0.00",
                'message': f"NEGATIVE PROFIT: Losing ${abs(row['GrossProfit']):.2f}",
                'recommendation': "URGENT: Review immediately - selling at a loss!"
            })
    
    return alerts

def check_inventory_alerts(df):
    """Check for inventory-related alerts"""
    alerts = []
    
    # Low stock turnover
    low_turnover = df[df['StockTurnover'] < AlertConfig.LOW_STOCK_TURNOVER]
    for _, row in low_turnover.iterrows():
        alerts.append({
            'type': AlertType.LOW_TURNOVER,
            'priority': AlertConfig.PRIORITY_MEDIUM,
            'vendor': row['VendorName'],
            'description': row['Description'],
            'metric_value': f"{row['StockTurnover']:.2f}x",
            'threshold': f"{AlertConfig.LOW_STOCK_TURNOVER}x",
            'message': f"Slow-moving inventory (turnover: {row['StockTurnover']:.2f}x)",
            'recommendation': "Consider discounting or promotional activities"
        })
    
    # Overstocked items
    if 'IsOverstocked' in df.columns:
        overstocked = df[df['IsOverstocked'] == True]
        for _, row in overstocked.iterrows():
            alerts.append({
                'type': AlertType.OVERSTOCKED,
                'priority': AlertConfig.PRIORITY_HIGH,
                'vendor': row['VendorName'],
                'description': row['Description'],
                'metric_value': f"${row['TotalPurchaseDollars']:.2f}",
                'threshold': "Optimal level",
                'message': f"Overstocked - excessive inventory value",
                'recommendation': "Reduce ordering, consider clearance sale"
            })
    
    # Understocked items
    if 'IsUnderstocked' in df.columns:
        understocked = df[df['IsUnderstocked'] == True]
        for _, row in understocked.iterrows():
            alerts.append({
                'type': AlertType.UNDERSTOCKED,
                'priority': AlertConfig.PRIORITY_CRITICAL,
                'vendor': row['VendorName'],
                'description': row['Description'],
                'metric_value': f"${row['TotalPurchaseDollars']:.2f}",
                'threshold': "Reorder point",
                'message': f"Stock level critically low",
                'recommendation': "URGENT: Reorder immediately to avoid stockout"
            })
    
    # High inventory value
    high_value = df[df['TotalPurchaseDollars'] > AlertConfig.HIGH_INVENTORY_VALUE]
    for _, row in high_value.head(10).iterrows():  # Top 10 only
        alerts.append({
            'type': AlertType.HIGH_INVENTORY,
            'priority': AlertConfig.PRIORITY_LOW,
            'vendor': row['VendorName'],
            'description': row['Description'],
            'metric_value': f"${row['TotalPurchaseDollars']:.2f}",
            'threshold': f"${AlertConfig.HIGH_INVENTORY_VALUE}",
            'message': f"High inventory value - monitor closely",
            'recommendation': "Track closely to ensure adequate return on investment"
        })
    
    return alerts

def check_performance_alerts(df):
    """Check for performance-related alerts"""
    alerts = []
    
    # Poor performance scores
    if 'PerformanceScore' in df.columns:
        poor_performers = df[df['PerformanceScore'] < AlertConfig.POOR_PERFORMANCE_SCORE]
        for _, row in poor_performers.iterrows():
            alerts.append({
                'type': AlertType.POOR_PERFORMANCE,
                'priority': AlertConfig.PRIORITY_HIGH,
                'vendor': row['VendorName'],
                'description': row['Description'],
                'metric_value': f"{row['PerformanceScore']:.1f}/100",
                'threshold': f"{AlertConfig.POOR_PERFORMANCE_SCORE}/100",
                'message': f"Poor overall performance score ({row['PerformanceScore']:.1f}/100)",
                'recommendation': "Review vendor relationship - consider alternatives"
            })
    
    # Anomalies
    if 'AnomalyScore' in df.columns:
        anomalies = df[df['AnomalyScore'] < AlertConfig.ANOMALY_SCORE_THRESHOLD]
        for _, row in anomalies.iterrows():
            alerts.append({
                'type': AlertType.ANOMALY,
                'priority': AlertConfig.PRIORITY_MEDIUM,
                'vendor': row['VendorName'],
                'description': row['Description'],
                'metric_value': f"{row['AnomalyScore']:.2f}",
                'threshold': f"{AlertConfig.ANOMALY_SCORE_THRESHOLD}",
                'message': f"Unusual behavior pattern detected",
                'recommendation': "Investigate for data quality issues or exceptional circumstances"
            })
    
    return alerts

def generate_all_alerts():
    """Generate all alerts based on current data"""
    logging.info("🔔 Starting alert generation...")
    
    df = load_data_for_alerts()
    if df is None:
        return []
    
    all_alerts = []
    
    # Check different alert types
    all_alerts.extend(check_profit_alerts(df))
    all_alerts.extend(check_inventory_alerts(df))
    all_alerts.extend(check_performance_alerts(df))
    
    # Add timestamp
    for alert in all_alerts:
        alert['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        alert['alert_id'] = f"ALT_{datetime.now().strftime('%Y%m%d%H%M%S')}_{len(all_alerts)}"
    
    logging.info(f"🔔 Generated {len(all_alerts)} alerts")
    
    # Save to database
    if all_alerts:
        alerts_df = pd.DataFrame(all_alerts)
        alerts_df.to_sql('active_alerts', engine, if_exists='replace', index=False)
        
        # Also append to alert history
        try:
            alerts_df.to_sql('alert_history', engine, if_exists='append', index=False)
        except:
            alerts_df.to_sql('alert_history', engine, if_exists='replace', index=False)
    
    return all_alerts

# ================== EMAIL NOTIFICATIONS ==================
def send_email_alert(alerts, recipient=None):
    """Send email notification with alerts"""
    
    if not alerts:
        logging.info("✅ No alerts to send")
        return True
    
    # Check if email is configured
    if AlertConfig.SENDER_EMAIL == "your-email@gmail.com":
        logging.warning("⚠️ Email not configured - skipping email notification")
        logging.info("💡 Configure email settings in AlertConfig to enable email alerts")
        return False
    
    try:
        # Group alerts by priority
        critical = [a for a in alerts if a['priority'] == AlertConfig.PRIORITY_CRITICAL]
        high = [a for a in alerts if a['priority'] == AlertConfig.PRIORITY_HIGH]
        medium = [a for a in alerts if a['priority'] == AlertConfig.PRIORITY_MEDIUM]
        low = [a for a in alerts if a['priority'] == AlertConfig.PRIORITY_LOW]
        
        # Create email content
        html_content = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .header {{ background: linear-gradient(90deg, #667eea, #764ba2); color: white; padding: 20px; }}
                .alert {{ margin: 15px 0; padding: 15px; border-left: 4px solid; }}
                .critical {{ background: #fee; border-color: #c00; }}
                .high {{ background: #ffe; border-color: #f80; }}
                .medium {{ background: #ffc; border-color: #fa0; }}
                .low {{ background: #efe; border-color: #0a0; }}
                .footer {{ color: #666; font-size: 12px; margin-top: 30px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🔔 Vendor Performance Alerts</h1>
                <p>{datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
            </div>
            
            <h2>📊 Alert Summary</h2>
            <p>
                🔴 Critical: {len(critical)} | 
                🟠 High: {len(high)} | 
                🟡 Medium: {len(medium)} | 
                🟢 Low: {len(low)}
            </p>
        """
        
        # Add critical alerts
        if critical:
            html_content += "<h2>🔴 CRITICAL ALERTS</h2>"
            for alert in critical[:10]:  # Top 10 critical
                html_content += f"""
                <div class="alert critical">
                    <strong>{alert['type']}</strong><br>
                    <strong>Vendor:</strong> {alert['vendor']}<br>
                    <strong>Item:</strong> {alert['description']}<br>
                    <strong>Issue:</strong> {alert['message']}<br>
                    <strong>Action:</strong> {alert['recommendation']}
                </div>
                """
        
        # Add high priority alerts
        if high:
            html_content += "<h2>🟠 HIGH PRIORITY ALERTS</h2>"
            for alert in high[:10]:  # Top 10 high
                html_content += f"""
                <div class="alert high">
                    <strong>{alert['type']}</strong><br>
                    <strong>Vendor:</strong> {alert['vendor']}<br>
                    <strong>Item:</strong> {alert['description']}<br>
                    <strong>Issue:</strong> {alert['message']}<br>
                    <strong>Action:</strong> {alert['recommendation']}
                </div>
                """
        
        html_content += f"""
            <div class="footer">
                <p>This is an automated alert from your Vendor Analytics System.</p>
                <p>Total alerts: {len(alerts)} | Critical: {len(critical)} need immediate attention</p>
            </div>
        </body>
        </html>
        """
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"🔔 Vendor Alert: {len(critical)} Critical, {len(high)} High Priority"
        msg['From'] = AlertConfig.SENDER_EMAIL
        msg['To'] = recipient or ", ".join(AlertConfig.RECIPIENT_EMAILS)
        
        # Attach HTML content
        html_part = MIMEText(html_content, 'html')
        msg.attach(html_part)
        
        # Send email
        with smtplib.SMTP(AlertConfig.SMTP_SERVER, AlertConfig.SMTP_PORT) as server:
            server.starttls()
            server.login(AlertConfig.SENDER_EMAIL, AlertConfig.SENDER_PASSWORD)
            server.send_message(msg)
        
        logging.info(f"✅ Email alert sent to {msg['To']}")
        return True
        
    except Exception as e:
        logging.error(f"❌ Failed to send email: {str(e)}")
        return False

# ================== ALERT SUMMARY ==================
def print_alert_summary(alerts):
    """Print a summary of alerts to console"""
    
    if not alerts:
        print("\n✅ No alerts - all systems normal!")
        return
    
    # Group by priority
    critical = [a for a in alerts if a['priority'] == AlertConfig.PRIORITY_CRITICAL]
    high = [a for a in alerts if a['priority'] == AlertConfig.PRIORITY_HIGH]
    medium = [a for a in alerts if a['priority'] == AlertConfig.PRIORITY_MEDIUM]
    low = [a for a in alerts if a['priority'] == AlertConfig.PRIORITY_LOW]
    
    print("\n" + "="*70)
    print("🔔 ALERT SUMMARY")
    print("="*70)
    print(f"Total Alerts: {len(alerts)}")
    print(f"🔴 Critical: {len(critical)}")
    print(f"🟠 High: {len(high)}")
    print(f"🟡 Medium: {len(medium)}")
    print(f"🟢 Low: {len(low)}")
    print("="*70)
    
    # Show critical alerts
    if critical:
        print("\n🔴 CRITICAL ALERTS (Action Required IMMEDIATELY):")
        for i, alert in enumerate(critical[:5], 1):
            print(f"\n{i}. {alert['type']}")
            print(f"   Vendor: {alert['vendor']}")
            print(f"   Item: {alert['description']}")
            print(f"   Issue: {alert['message']}")
            print(f"   Action: {alert['recommendation']}")
    
    # Show high priority alerts
    if high:
        print("\n🟠 HIGH PRIORITY ALERTS (Action Required Soon):")
        for i, alert in enumerate(high[:5], 1):
            print(f"\n{i}. {alert['type']}")
            print(f"   Vendor: {alert['vendor']}")
            print(f"   Issue: {alert['message']}")
    
    print("\n💡 View all alerts in the Alert Dashboard")
    print("="*70 + "\n")

# ================== MAIN ALERT RUNNER ==================
def run_alert_system(send_email=False):
    """Run the complete alert system"""
    logging.info("="*70)
    logging.info(f"🔔 ALERT SYSTEM STARTED: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logging.info("="*70)
    
    # Generate alerts
    alerts = generate_all_alerts()
    
    # Print summary
    print_alert_summary(alerts)
    
    # Send email if requested and alerts exist
    if send_email and alerts:
        logging.info("📧 Sending email notification...")
        send_email_alert(alerts)
    
    logging.info("="*70)
    logging.info(f"✅ ALERT SYSTEM COMPLETED")
    logging.info(f"📊 Generated: {len(alerts)} alerts")
    logging.info("="*70)
    
    return alerts

# ================== ENTRY POINT ==================
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Real-Time Alert System')
    parser.add_argument('--email', action='store_true', help='Send email notifications')
    parser.add_argument('--test', action='store_true', help='Test email configuration')
    
    args = parser.parse_args()
    
    if args.test:
        print("📧 Testing email configuration...")
        test_alerts = [{
            'type': 'Test Alert',
            'priority': AlertConfig.PRIORITY_LOW,
            'vendor': 'Test Vendor',
            'description': 'Test Item',
            'metric_value': 'N/A',
            'threshold': 'N/A',
            'message': 'This is a test alert',
            'recommendation': 'No action needed - this is a test',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'alert_id': 'TEST_001'
        }]
        send_email_alert(test_alerts)
    else:
        run_alert_system(send_email=args.email)
