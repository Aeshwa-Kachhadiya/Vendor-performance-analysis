import pandas as pd
import numpy as np

print("📊 Creating vendor_sales_summary from sales and purchases data...")

# Load the exported CSVs
try:
    sales_df = pd.read_csv('sales.csv')
    purchases_df = pd.read_csv('purchases.csv')
    print(f"✅ Loaded sales: {len(sales_df)} rows")
    print(f"✅ Loaded purchases: {len(purchases_df)} rows")
except Exception as e:
    print(f"❌ Error loading files: {e}")
    exit()

# Group sales data
sales_summary = sales_df.groupby(['VendorName', 'Description']).agg({
    'SalesQuantity': 'sum',
    'SalesDollars': 'sum'
}).reset_index()

sales_summary.columns = ['VendorName', 'Description', 'TotalSalesQuantity', 'TotalSalesDollars']

# Group purchases data
purchases_summary = purchases_df.groupby(['VendorName', 'Description']).agg({
    'PurchaseQuantity': 'sum',
    'PurchaseDollars': 'sum'
}).reset_index()

purchases_summary.columns = ['VendorName', 'Description', 'TotalPurchaseQuantity', 'TotalPurchaseDollars']

# Merge sales and purchases
vendor_summary = pd.merge(
    sales_summary,
    purchases_summary,
    on=['VendorName', 'Description'],
    how='outer'
).fillna(0)

# Calculate metrics
vendor_summary['GrossProfit'] = vendor_summary['TotalSalesDollars'] - vendor_summary['TotalPurchaseDollars']
vendor_summary['ProfitMargin'] = np.where(
    vendor_summary['TotalSalesDollars'] > 0,
    (vendor_summary['GrossProfit'] / vendor_summary['TotalSalesDollars']) * 100,
    0
)
vendor_summary['StockTurnover'] = np.where(
    vendor_summary['TotalPurchaseQuantity'] > 0,
    vendor_summary['TotalSalesQuantity'] / vendor_summary['TotalPurchaseQuantity'],
    0
)
vendor_summary['SalesToPurchaseRatio'] = np.where(
    vendor_summary['TotalPurchaseDollars'] > 0,
    vendor_summary['TotalSalesDollars'] / vendor_summary['TotalPurchaseDollars'],
    0
)

# Filter out invalid data
vendor_summary = vendor_summary[
    (vendor_summary['GrossProfit'] > 0) &
    (vendor_summary['ProfitMargin'] > 0) &
    (vendor_summary['TotalSalesQuantity'] > 0)
]

# Save to CSV
vendor_summary.to_csv('vendor_sales_summary.csv', index=False)

print(f"\n✅ Created vendor_sales_summary.csv with {len(vendor_summary)} rows!")
print(f"📊 Columns: {list(vendor_summary.columns)}")
print("\n🎉 All done! Now you have all 3 CSV files ready for upload.")
