"""
Automated Data Pipeline for Vendor Analytics
Handles data ingestion, transformation, and database updates
"""

import pandas as pd
import os
from sqlalchemy import create_engine, text
import logging
import time
from datetime import datetime
import schedule
from pathlib import Path
import shutil

# ================== LOGGING CONFIGURATION ==================
log_dir = Path('logs')
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    filename='logs/pipeline.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filemode='a',
    encoding='utf-8'
)

console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

# ================== DATABASE CONFIGURATION ==================
engine = create_engine("sqlite:///inventory.db")

# ================== DATA INGESTION ==================
def ingest_raw_data(df, table_name, engine):
    """Ingest dataframe into database table"""
    try:
        df.to_sql(table_name, con=engine, if_exists='replace', index=False)
        logging.info(f"✅ Ingested {table_name}: {df.shape[0]} rows, {df.shape[1]} cols")
        return True
    except Exception as e:
        logging.error(f"❌ Failed to ingest {table_name}: {str(e)}")
        return False

def load_excel_files():
    """Load all Excel files from data folder"""
    start_time = time.time()
    data_folder = Path('data')
    
    if not data_folder.exists():
        logging.error(f"❌ Data folder not found: {data_folder}")
        return False
    
    excel_files = list(data_folder.glob('*.xlsx'))
    
    if not excel_files:
        logging.warning("⚠️ No Excel files found in data folder")
        return False
    
    logging.info(f"📁 Found {len(excel_files)} Excel files")
    
    success_count = 0
    for file_path in excel_files:
        try:
            logging.info(f"📥 Processing: {file_path.name}")
            df = pd.read_excel(file_path)
            table_name = file_path.stem  # filename without extension
            
            if ingest_raw_data(df, table_name, engine):
                success_count += 1
        except Exception as e:
            logging.error(f"❌ Error processing {file_path.name}: {str(e)}")
    
    elapsed_time = (time.time() - start_time) / 60
    logging.info(f"✅ Ingestion complete: {success_count}/{len(excel_files)} files")
    logging.info(f"⏱️ Time taken: {elapsed_time:.2f} minutes")
    
    return success_count > 0

# ================== DATA TRANSFORMATION ==================
def create_vendor_summary():
    """Create vendor sales summary view"""
    try:
        query = """
        CREATE TABLE IF NOT EXISTS vendor_sales_summary AS
        SELECT 
            s.VendorName,
            s.Description,
            SUM(s.SalesQuantity) AS TotalSalesQuantity,
            SUM(s.SalesDollars) AS TotalSalesDollars,
            SUM(p.PurchaseQuantity) AS TotalPurchaseQuantity,
            SUM(p.PurchaseDollars) AS TotalPurchaseDollars,
            (SUM(s.SalesDollars) - SUM(p.PurchaseDollars)) AS GrossProfit,
            CASE 
                WHEN SUM(s.SalesDollars) > 0 
                THEN ((SUM(s.SalesDollars) - SUM(p.PurchaseDollars)) / SUM(s.SalesDollars)) * 100
                ELSE 0 
            END AS ProfitMargin,
            CASE 
                WHEN AVG(p.PurchaseQuantity) > 0 
                THEN SUM(s.SalesQuantity) / AVG(p.PurchaseQuantity)
                ELSE 0 
            END AS StockTurnover,
            CASE 
                WHEN SUM(p.PurchaseDollars) > 0 
                THEN SUM(s.SalesDollars) / SUM(p.PurchaseDollars)
                ELSE 0 
            END AS SalesToPurchaseRatio
        FROM sales s
        LEFT JOIN purchases p 
            ON s.VendorName = p.VendorName 
            AND s.Description = p.Description
        GROUP BY s.VendorName, s.Description
        HAVING SUM(s.SalesDollars) > 0 
            AND SUM(p.PurchaseDollars) > 0
        """
        
        with engine.connect() as conn:
            # Drop existing table
            conn.execute(text("DROP TABLE IF EXISTS vendor_sales_summary"))
            conn.commit()
            
            # Create new summary
            conn.execute(text(query))
            conn.commit()
        
        logging.info("✅ Vendor summary table created successfully")
        return True
    except Exception as e:
        logging.error(f"❌ Failed to create vendor summary: {str(e)}")
        return False

def validate_data():
    """Validate data quality and integrity"""
    issues = []
    
    try:
        with engine.connect() as conn:
            # Check if required tables exist
            tables = ['sales', 'purchases']
            for table in tables:
                result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = result.scalar()
                if count == 0:
                    issues.append(f"⚠️ Table '{table}' is empty")
                else:
                    logging.info(f"✅ Table '{table}': {count} records")
            
            # Check for negative values
            result = conn.execute(text(
                "SELECT COUNT(*) FROM sales WHERE SalesDollars < 0"
            ))
            neg_sales = result.scalar()
            if neg_sales > 0:
                issues.append(f"⚠️ Found {neg_sales} negative sales values")
            
            result = conn.execute(text(
                "SELECT COUNT(*) FROM purchases WHERE PurchaseDollars < 0"
            ))
            neg_purchases = result.scalar()
            if neg_purchases > 0:
                issues.append(f"⚠️ Found {neg_purchases} negative purchase values")
    
    except Exception as e:
        logging.error(f"❌ Validation failed: {str(e)}")
        return False
    
    if issues:
        for issue in issues:
            logging.warning(issue)
        return False
    
    logging.info("✅ Data validation passed")
    return True

# ================== ARCHIVE MANAGEMENT ==================
def archive_processed_files():
    """Move processed files to archive folder"""
    data_folder = Path('data')
    archive_folder = Path('data/archive')
    archive_folder.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    for file_path in data_folder.glob('*.xlsx'):
        try:
            archive_name = f"{file_path.stem}_{timestamp}{file_path.suffix}"
            archive_path = archive_folder / archive_name
            shutil.move(str(file_path), str(archive_path))
            logging.info(f"📦 Archived: {file_path.name} -> {archive_name}")
        except Exception as e:
            logging.error(f"❌ Failed to archive {file_path.name}: {str(e)}")

# ================== MAIN PIPELINE ==================
def run_pipeline(archive=False):
    """Execute the complete data pipeline"""
    logging.info("=" * 70)
    logging.info(f"🚀 PIPELINE STARTED: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logging.info("=" * 70)
    
    pipeline_start = time.time()
    
    # Step 1: Load raw data
    logging.info("📥 Step 1: Loading raw data...")
    if not load_excel_files():
        logging.error("❌ Pipeline failed: Data loading error")
        return False
    
    # Step 2: Validate data
    logging.info("🔍 Step 2: Validating data...")
    if not validate_data():
        logging.warning("⚠️ Data validation issues detected, but continuing...")
    
    # Step 3: Create transformations
    logging.info("🔄 Step 3: Creating vendor summary...")
    if not create_vendor_summary():
        logging.error("❌ Pipeline failed: Transformation error")
        return False
    
    # Step 4: Archive files (optional)
    if archive:
        logging.info("📦 Step 4: Archiving processed files...")
        archive_processed_files()
    
    elapsed_time = (time.time() - pipeline_start) / 60
    logging.info("=" * 70)
    logging.info(f"✅ PIPELINE COMPLETED: {elapsed_time:.2f} minutes")
    logging.info("=" * 70)
    
    return True

# ================== SCHEDULING ==================
def schedule_pipeline(interval_hours=24):
    """Schedule pipeline to run at regular intervals"""
    logging.info(f"⏰ Scheduling pipeline to run every {interval_hours} hours")
    
    schedule.every(interval_hours).hours.do(lambda: run_pipeline(archive=True))
    
    logging.info("🔄 Scheduler started. Press Ctrl+C to stop.")
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        logging.info("⏹️ Scheduler stopped by user")

# ================== ENTRY POINT ==================
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Automated Data Pipeline')
    parser.add_argument('--schedule', type=int, help='Run on schedule (hours)', metavar='HOURS')
    parser.add_argument('--archive', action='store_true', help='Archive files after processing')
    parser.add_argument('--validate-only', action='store_true', help='Only run validation')
    
    args = parser.parse_args()
    
    if args.validate_only:
        validate_data()
    elif args.schedule:
        # Run once immediately, then schedule
        run_pipeline(archive=args.archive)
        schedule_pipeline(interval_hours=args.schedule)
    else:
        # Run once
        run_pipeline(archive=args.archive)
