"""
Barchart Options Dashboard - Streamlit Frontend
Connects to FastAPI backend for options data scraping.
"""
import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Page configuration - MUST be first
st.set_page_config(
    page_title="Barchart Options Dashboard",
    page_icon="📊",
    layout="wide"
)

# API Configuration
DEFAULT_API_URL = "http://localhost:8000"
try:
    API_BASE_URL = st.secrets.get("API_BASE_URL", DEFAULT_API_URL)
except:
    API_BASE_URL = DEFAULT_API_URL

# Barchart-inspired dark theme CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    * { font-family: 'Inter', sans-serif; }
    .main { background: #1a1d21; }
    .stApp { background: linear-gradient(180deg, #1a1d21 0%, #0d0f11 100%); }
    
    .header {
        background: linear-gradient(90deg, #00875a 0%, #00a86b 100%);
        padding: 1.5rem 2rem;
        margin: -1rem -1rem 1.5rem -1rem;
        border-radius: 0;
    }
    .header h1 { color: white; font-size: 1.8rem; font-weight: 700; margin: 0; }
    .header p { color: rgba(255,255,255,0.85); margin-top: 0.3rem; font-size: 0.9rem; }
    
    .status-ok {
        display: inline-flex; align-items: center; gap: 8px;
        padding: 0.4rem 0.8rem;
        background: rgba(0, 215, 117, 0.15);
        border: 1px solid #00d775;
        border-radius: 15px;
        color: #00d775;
        font-weight: 600;
        font-size: 0.8rem;
    }
    .status-error {
        display: inline-flex; align-items: center; gap: 8px;
        padding: 0.4rem 0.8rem;
        background: rgba(255, 71, 87, 0.15);
        border: 1px solid #ff4757;
        border-radius: 15px;
        color: #ff4757;
        font-weight: 600;
        font-size: 0.8rem;
    }
    
    .stButton > button {
        background: linear-gradient(90deg, #00875a 0%, #00a86b 100%);
        color: white;
        border: none;
        border-radius: 6px;
        font-weight: 600;
    }
    
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e2328 0%, #15181c 100%);
        border-right: 1px solid #3d4450;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


def check_api():
    """Check if API is available."""
    try:
        r = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return r.status_code == 200
    except:
        return False


@st.cache_data(ttl=300, show_spinner=False)
def fetch_options(symbol: str, date: str):
    """Fetch options data from API with proper error handling."""
    try:
        r = requests.get(
            f"{API_BASE_URL}/options",
            params={"symbol": symbol, "date": date},
            timeout=120
        )
        if r.status_code == 200:
            return {"success": True, "data": r.json()}
        else:
            # Parse error detail from API response
            try:
                error_detail = r.json().get('detail', 'Unknown error occurred')
            except:
                error_detail = f"HTTP {r.status_code}: Server error"
            
            return {
                "success": False, 
                "error": error_detail,
                "status_code": r.status_code
            }
    except requests.exceptions.Timeout:
        return {
            "success": False,
            "error": "Request timed out. The scraper may be taking too long. Please try again.",
            "status_code": 408
        }
    except requests.exceptions.ConnectionError:
        return {
            "success": False,
            "error": "Cannot connect to API server. Make sure the backend is running.",
            "status_code": 503
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "status_code": 500
        }


def create_charts(df):
    """Create visualization charts."""
    # Extract numeric values
    def parse_num(val):
        if pd.isna(val) or val == "": return 0
        return float(str(val).replace(",", ""))
    
    df["call_oi"] = df["Call OI"].apply(parse_num)
    df["put_oi"] = df["Put OI"].apply(parse_num)
    df["strike_num"] = df["Strike"].apply(parse_num)
    
    # Open Interest Chart
    fig = make_subplots(rows=1, cols=2, subplot_titles=('📈 Calls OI', '📉 Puts OI'))
    
    fig.add_trace(
        go.Bar(x=df['strike_num'], y=df['call_oi'], name='Calls', marker_color='#00d775'),
        row=1, col=1
    )
    fig.add_trace(
        go.Bar(x=df['strike_num'], y=df['put_oi'], name='Puts', marker_color='#ff4757'),
        row=1, col=2
    )
    
    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor='#1e2328',
        plot_bgcolor='#1e2328',
        font=dict(color='white'),
        height=350,
        showlegend=False
    )
    fig.update_xaxes(title_text="Strike", gridcolor='#3d4450')
    fig.update_yaxes(title_text="Open Interest", gridcolor='#3d4450')
    
    return fig


def main():
    # Header
    st.markdown("""
    <div class="header">
        <h1>📊 Barchart Options Dashboard</h1>
        <p>Scrape options data with symbol and date</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Check API
    api_ok = check_api()
    
    # Sidebar
    with st.sidebar:
        st.markdown("## 🔍 Options Query")
        
        symbol = st.text_input("Symbol", value="AAPL", help="Stock symbol (e.g., AAPL, TSLA, $SPX)")
        symbol = symbol.upper().strip()
        
        date = st.text_input("Expiration Date", value="2026-01-17", help="Format: YYYY-MM-DD or YYYY-MM-DD-w for weekly")
        
        fetch_btn = st.button("🔄 Fetch Data", use_container_width=True, disabled=not api_ok)
        
        st.markdown("---")
        
        st.markdown("### 🔥 Quick Symbols")
        popular = ['AAPL', 'TSLA', 'NVDA', 'SPY', 'QQQ', 'AMZN']
        cols = st.columns(3)
        for i, s in enumerate(popular):
            with cols[i % 3]:
                if st.button(s, key=f"q_{s}", use_container_width=True):
                    symbol = s
        
        st.markdown("---")
        
        # API Status
        if api_ok:
            st.markdown('<div class="status-ok">✓ API Connected</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="status-error">✗ API Offline</div>', unsafe_allow_html=True)
        
        st.caption(f"Backend: {API_BASE_URL}")
    
    # Main content
    if not api_ok:
        st.error(f"""
        **Cannot connect to API at `{API_BASE_URL}`**
        
        Start the backend:
        ```bash
        cd backend
        python -m uvicorn api:app --host 0.0.0.0 --port 8000
        ```
        """)
        return
    
    if fetch_btn or st.session_state.get("last_fetch"):
        st.session_state["last_fetch"] = {"symbol": symbol, "date": date}
        
        with st.spinner(f"Scraping {symbol} options for {date}... (this may take 30-60 seconds)"):
            result = fetch_options(symbol, date)
        
        # Handle errors
        if not result.get("success"):
            error_msg = result.get("error", "Unknown error occurred")
            status_code = result.get("status_code", 500)
            
            # Create user-friendly error display
            st.error(f"**⚠️ Failed to fetch options data**")
            
            # Error details in expander
            with st.expander("📋 Error Details", expanded=True):
                st.markdown(f"""
                **Error:** {error_msg}
                
                **Symbol:** `{symbol}` | **Date:** `{date}`
                """)
                
                # Troubleshooting tips based on error type
                if status_code == 404:
                    st.warning("""
                    **💡 Troubleshooting Tips:**
                    - Verify the stock symbol is correct (e.g., AAPL, TSLA, NVDA)
                    - Check if the expiration date exists for this symbol
                    - For weekly options, use format: `2026-01-10-w`
                    - Visit [Barchart Options](https://www.barchart.com/stocks/quotes/AAPL/options) to verify available dates
                    """)
                elif status_code == 408:
                    st.warning("""
                    **💡 Troubleshooting Tips:**
                    - The request timed out. This can happen if Barchart is slow.
                    - Try again in a few moments.
                    - Consider trying a different symbol.
                    """)
                elif status_code == 503:
                    st.warning("""
                    **💡 Troubleshooting Tips:**
                    - Make sure the backend API is running.
                    - Run: `cd backend && python -m uvicorn api:app --port 8000`
                    """)
                else:
                    st.warning("""
                    **💡 Troubleshooting Tips:**
                    - Check if the API server is running correctly
                    - Look at the backend logs for more details
                    - Try clearing cache and fetching again
                    """)
                
                # Clear cache button
                if st.button("🔄 Clear Cache & Retry"):
                    st.cache_data.clear()
                    st.rerun()
        
        elif result.get("data") and result["data"].get("success"):
            api_data = result["data"]
            data = api_data.get("data", [])
            count = api_data.get("count", len(data))
            df = pd.DataFrame(data)
            
            # Info bar
            st.success(f"✓ Loaded {count} strikes for **{symbol}** expiring **{date}**")
            
            # Tabs
            tab1, tab2 = st.tabs(["📋 Options Chain", "📊 Charts"])
            
            with tab1:
                # Table header
                st.markdown("""
                <div style="display: flex; margin-bottom: 0;">
                    <div style="flex: 1; background: linear-gradient(90deg, #00875a, #00a86b); color: white; padding: 10px; text-align: center; font-weight: 600; border-radius: 8px 0 0 0;">
                        📈 CALLS
                    </div>
                    <div style="flex: 0 0 80px; background: #3d4450; color: white; padding: 10px; text-align: center; font-weight: 600;">
                        STRIKE
                    </div>
                    <div style="flex: 1; background: linear-gradient(90deg, #dc3545, #ff4757); color: white; padding: 10px; text-align: center; font-weight: 600; border-radius: 0 8px 0 0;">
                        📉 PUTS
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                st.dataframe(df, use_container_width=True, height=500, hide_index=True)
                
                # Download buttons
                col1, col2 = st.columns(2)
                with col1:
                    csv = df.to_csv(index=False)
                    st.download_button(
                        "📥 Download CSV",
                        data=csv,
                        file_name=f"options_{symbol}_{date}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                with col2:
                    st.markdown(f"[📥 Direct API CSV]({API_BASE_URL}/options/csv?symbol={symbol}&date={date})")
            
            with tab2:
                fig = create_charts(df)
                st.plotly_chart(fig, use_container_width=True)
                
                # Summary
                def parse_num(val):
                    if pd.isna(val) or val == "": return 0
                    return float(str(val).replace(",", ""))
                
                total_call_oi = sum(parse_num(v) for v in df["Call OI"])
                total_put_oi = sum(parse_num(v) for v in df["Put OI"])
                pc_ratio = total_put_oi / total_call_oi if total_call_oi > 0 else 0
                
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Total Call OI", f"{total_call_oi:,.0f}")
                c2.metric("Total Put OI", f"{total_put_oi:,.0f}")
                c3.metric("P/C Ratio", f"{pc_ratio:.3f}")
                c4.metric("Sentiment", "🐂 Bullish" if pc_ratio < 1 else "🐻 Bearish")
    
    else:
        st.info("👆 Enter a symbol and date, then click **Fetch Data** to load options chain.")
    
    # Footer
    st.markdown("---")
    st.caption("📊 Barchart Options Dashboard | Data scraped from Barchart.com | For educational purposes only")


if __name__ == "__main__":
    main()
