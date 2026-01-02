"""
Vendor Analytics Dashboard - Interactive Streamlit Application
Author: Your Name
Description: Real-time vendor performance monitoring and analytics
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sqlite3
from datetime import datetime, timedelta
import numpy as np

# ================== PAGE CONFIGURATION ==================
st.set_page_config(
    page_title="📊 Vendor Analytics Dashboard",
    page_layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "Vendor Consolidation & Profit Optimization Platform"
    }
)

# ================== CUSTOM CSS STYLING ==================
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 20px 0;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    }
    .stMetric {
        background-color: white;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# ================== DATABASE CONNECTION ==================
@st.cache_resource
def get_database_connection():
    """Create a cached database connection"""
    try:
        conn = sqlite3.connect('inventory.db', check_same_thread=False)
        return conn
    except Exception as e:
        st.error(f"❌ Database connection failed: {e}")
        return None

# ================== DATA LOADING FUNCTIONS ==================
@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_vendor_summary():
    """Load vendor sales summary data"""
    conn = get_database_connection()
    if conn:
        query = """
        SELECT * FROM vendor_sales_summary
        WHERE GrossProfit > 0 
        AND ProfitMargin > 0 
        AND TotalSalesQuantity > 0
        """
        df = pd.read_sql_query(query, conn)
        return df
    return pd.DataFrame()

@st.cache_data(ttl=300)
def load_purchases_data():
    """Load purchases data"""
    conn = get_database_connection()
    if conn:
        df = pd.read_sql_query("SELECT * FROM purchases", conn)
        return df
    return pd.DataFrame()

@st.cache_data(ttl=300)
def load_sales_data():
    """Load sales data"""
    conn = get_database_connection()
    if conn:
        df = pd.read_sql_query("SELECT * FROM sales", conn)
        return df
    return pd.DataFrame()

# ================== HELPER FUNCTIONS ==================
def format_currency(value):
    """Format numbers as currency"""
    if value >= 1_000_000:
        return f"${value/1_000_000:.2f}M"
    elif value >= 1_000:
        return f"${value/1_000:.2f}K"
    else:
        return f"${value:.2f}"

def calculate_kpis(df):
    """Calculate key performance indicators"""
    total_sales = df['TotalSalesDollars'].sum()
    total_purchases = df['TotalPurchaseDollars'].sum()
    total_profit = df['GrossProfit'].sum()
    avg_margin = df['ProfitMargin'].mean()
    avg_turnover = df['StockTurnover'].mean()
    
    return {
        'total_sales': total_sales,
        'total_purchases': total_purchases,
        'total_profit': total_profit,
        'avg_margin': avg_margin,
        'avg_turnover': avg_turnover
    }

# ================== MAIN DASHBOARD ==================
def main():
    # Header
    st.markdown('<h1 class="main-header">📊 Vendor Analytics Dashboard</h1>', 
                unsafe_allow_html=True)
    st.markdown("---")
    
    # Load data
    with st.spinner("📥 Loading data..."):
        df = load_vendor_summary()
    
    if df.empty:
        st.error("⚠️ No data available. Please check your database connection.")
        return
    
    # ================== SIDEBAR FILTERS ==================
    st.sidebar.header("🔍 Filters")
    
    # Vendor filter
    all_vendors = sorted(df['VendorName'].unique().tolist())
    selected_vendors = st.sidebar.multiselect(
        "Select Vendors",
        options=all_vendors,
        default=all_vendors[:10] if len(all_vendors) > 10 else all_vendors
    )
    
    # Profit margin filter
    margin_range = st.sidebar.slider(
        "Profit Margin Range (%)",
        min_value=float(df['ProfitMargin'].min()),
        max_value=float(df['ProfitMargin'].max()),
        value=(float(df['ProfitMargin'].min()), float(df['ProfitMargin'].max()))
    )
    
    # Sales range filter
    sales_range = st.sidebar.slider(
        "Sales Range ($)",
        min_value=float(df['TotalSalesDollars'].min()),
        max_value=float(df['TotalSalesDollars'].max()),
        value=(float(df['TotalSalesDollars'].min()), float(df['TotalSalesDollars'].max()))
    )
    
    # Stock turnover filter
    turnover_threshold = st.sidebar.slider(
        "Minimum Stock Turnover",
        min_value=0.0,
        max_value=float(df['StockTurnover'].max()),
        value=0.0,
        step=0.1
    )
    
    # Apply filters
    filtered_df = df[
        (df['VendorName'].isin(selected_vendors)) &
        (df['ProfitMargin'].between(margin_range[0], margin_range[1])) &
        (df['TotalSalesDollars'].between(sales_range[0], sales_range[1])) &
        (df['StockTurnover'] >= turnover_threshold)
    ]
    
    # ================== KPI METRICS ==================
    st.subheader("📈 Key Performance Indicators")
    
    kpis = calculate_kpis(filtered_df)
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            label="💰 Total Sales",
            value=format_currency(kpis['total_sales']),
            delta=f"{(kpis['total_sales']/df['TotalSalesDollars'].sum())*100:.1f}% of total"
        )
    
    with col2:
        st.metric(
            label="🛒 Total Purchases",
            value=format_currency(kpis['total_purchases']),
            delta=f"{(kpis['total_purchases']/df['TotalPurchaseDollars'].sum())*100:.1f}% of total"
        )
    
    with col3:
        st.metric(
            label="💵 Gross Profit",
            value=format_currency(kpis['total_profit']),
            delta=f"{(kpis['total_profit']/kpis['total_sales'])*100:.1f}% margin"
        )
    
    with col4:
        st.metric(
            label="📊 Avg Profit Margin",
            value=f"{kpis['avg_margin']:.2f}%",
            delta=f"{kpis['avg_margin'] - df['ProfitMargin'].mean():.2f}% vs overall"
        )
    
    with col5:
        st.metric(
            label="🔄 Avg Turnover",
            value=f"{kpis['avg_turnover']:.2f}x",
            delta=f"{kpis['avg_turnover'] - df['StockTurnover'].mean():.2f}x vs overall"
        )
    
    st.markdown("---")
    
    # ================== VISUALIZATIONS ==================
    
    # Row 1: Sales vs Profit Margin & Top Vendors
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("💹 Sales vs Profit Margin Analysis")
        fig_scatter = px.scatter(
            filtered_df,
            x='TotalSalesDollars',
            y='ProfitMargin',
            size='TotalPurchaseQuantity',
            color='VendorName',
            hover_data=['Description', 'StockTurnover'],
            title="Sales Performance vs Profitability",
            labels={
                'TotalSalesDollars': 'Total Sales ($)',
                'ProfitMargin': 'Profit Margin (%)'
            }
        )
        fig_scatter.update_layout(height=500, showlegend=True)
        st.plotly_chart(fig_scatter, use_container_width=True)
    
    with col2:
        st.subheader("🏆 Top 10 Vendors by Sales")
        top_vendors = filtered_df.groupby('VendorName')['TotalSalesDollars'].sum().nlargest(10).reset_index()
        fig_bar = px.bar(
            top_vendors,
            x='TotalSalesDollars',
            y='VendorName',
            orientation='h',
            title="Highest Performing Vendors",
            labels={'TotalSalesDollars': 'Total Sales ($)', 'VendorName': 'Vendor'},
            color='TotalSalesDollars',
            color_continuous_scale='Blues'
        )
        fig_bar.update_layout(height=500)
        st.plotly_chart(fig_bar, use_container_width=True)
    
    # Row 2: Profit Distribution & Stock Turnover
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Profit Margin Distribution")
        fig_hist = px.histogram(
            filtered_df,
            x='ProfitMargin',
            nbins=30,
            title="Distribution of Profit Margins",
            labels={'ProfitMargin': 'Profit Margin (%)'},
            color_discrete_sequence=['#1f77b4']
        )
        fig_hist.update_layout(height=400)
        st.plotly_chart(fig_hist, use_container_width=True)
    
    with col2:
        st.subheader("🔄 Stock Turnover Analysis")
        fig_turnover = px.box(
            filtered_df,
            y='StockTurnover',
            x='VendorName',
            title="Stock Turnover by Vendor",
            labels={'StockTurnover': 'Stock Turnover Rate', 'VendorName': 'Vendor'}
        )
        fig_turnover.update_xaxes(tickangle=45)
        fig_turnover.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig_turnover, use_container_width=True)
    
    # Row 3: Vendor Performance Matrix
    st.subheader("📋 Vendor Performance Matrix")
    
    # Create performance segments
    filtered_df['PerformanceSegment'] = pd.cut(
        filtered_df['ProfitMargin'],
        bins=[0, 25, 50, 75, 100],
        labels=['Low', 'Medium', 'High', 'Excellent']
    )
    
    fig_sunburst = px.sunburst(
        filtered_df,
        path=['PerformanceSegment', 'VendorName'],
        values='TotalSalesDollars',
        title="Vendor Segmentation by Performance",
        color='ProfitMargin',
        color_continuous_scale='RdYlGn'
    )
    fig_sunburst.update_layout(height=600)
    st.plotly_chart(fig_sunburst, use_container_width=True)
    
    # ================== DATA TABLE ==================
    st.subheader("📑 Detailed Vendor Data")
    
    # Add search functionality
    search_term = st.text_input("🔍 Search by vendor or product name:", "")
    
    if search_term:
        display_df = filtered_df[
            filtered_df['VendorName'].str.contains(search_term, case=False, na=False) |
            filtered_df['Description'].str.contains(search_term, case=False, na=False)
        ]
    else:
        display_df = filtered_df
    
    # Select columns to display
    display_columns = [
        'VendorName', 'Description', 'TotalSalesDollars', 'TotalPurchaseDollars',
        'GrossProfit', 'ProfitMargin', 'StockTurnover', 'SalesToPurchaseRatio'
    ]
    
    # Format the dataframe
    styled_df = display_df[display_columns].copy()
    styled_df['TotalSalesDollars'] = styled_df['TotalSalesDollars'].apply(format_currency)
    styled_df['TotalPurchaseDollars'] = styled_df['TotalPurchaseDollars'].apply(format_currency)
    styled_df['GrossProfit'] = styled_df['GrossProfit'].apply(format_currency)
    styled_df['ProfitMargin'] = styled_df['ProfitMargin'].apply(lambda x: f"{x:.2f}%")
    styled_df['StockTurnover'] = styled_df['StockTurnover'].apply(lambda x: f"{x:.2f}x")
    styled_df['SalesToPurchaseRatio'] = styled_df['SalesToPurchaseRatio'].apply(lambda x: f"{x:.2f}")
    
    st.dataframe(
        styled_df,
        use_container_width=True,
        height=400
    )
    
    # Download button
    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Filtered Data as CSV",
        data=csv,
        file_name=f"vendor_analytics_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )
    
    # ================== INSIGHTS SECTION ==================
    st.markdown("---")
    st.subheader("💡 Key Insights & Recommendations")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("""
        **🎯 Top Performers**
        
        Focus on vendors with:
        - High profit margins (>50%)
        - Good stock turnover (>0.5x)
        - Consistent sales volume
        """)
    
    with col2:
        st.warning("""
        **⚠️ Areas of Concern**
        
        Monitor vendors with:
        - Low turnover (<0.2x)
        - Declining profit margins
        - Excess inventory
        """)
    
    with col3:
        st.success("""
        **✅ Optimization Opportunities**
        
        Consider:
        - Bulk purchase discounts
        - Contract renegotiations
        - Vendor consolidation
        """)
    
    # Footer
    st.markdown("---")
    st.caption(f"📅 Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    st.caption("💻 Built with Streamlit | 📊 Data from inventory.db")

# ================== RUN APPLICATION ==================
if __name__ == "__main__":
    main()
