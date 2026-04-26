import streamlit as st
import sqlite3
import pandas as pd
import altair as alt

# Set page config for a premium wide layout
st.set_page_config(page_title="Global Patent Intelligence Dashboard", page_icon="🌍", layout="wide")

# Custom CSS for premium feel
st.markdown("""
<style>
    .main .block-container {
        padding-top: 2rem;
    }
    h1 {
        color: #1E88E5;
        font-family: 'Inter', sans-serif;
    }
    .metric-card {
        background-color: #1E1E1E;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #42A5F5;
    }
    .metric-label {
        font-size: 1rem;
        color: #B0BEC5;
    }
</style>
""", unsafe_allow_html=True)

st.title("🌍 Global Patent Intelligence Data Pipeline")
st.markdown("Explore real-world patent innovation trends across inventors, corporations, and global regions.")

@st.cache_data
def load_data():
    conn = sqlite3.connect("patents.db")
    
    # Patents over time
    df_patents = pd.read_sql_query("SELECT year, COUNT(patent_id) as total_patents FROM patents WHERE year IS NOT NULL AND year > 1900 GROUP BY year ORDER BY year", conn)
    
    # Top Inventors
    q_inv = """
    SELECT i.name as Inventor, COUNT(DISTINCT r.patent_id) AS total_patents
    FROM inventors i JOIN relationships r ON i.inventor_id = r.inventor_id
    GROUP BY i.inventor_id, i.name ORDER BY total_patents DESC LIMIT 10;
    """
    df_inv = pd.read_sql_query(q_inv, conn)
    
    # Top Companies
    q_comp = """
    SELECT c.name as Company, COUNT(DISTINCT r.patent_id) AS total_patents
    FROM companies c JOIN relationships r ON c.company_id = r.company_id
    WHERE c.name IS NOT NULL
    GROUP BY c.company_id, c.name ORDER BY total_patents DESC LIMIT 10;
    """
    df_comp = pd.read_sql_query(q_comp, conn)
    
    # Top Countries
    q_cntry = """
    SELECT i.country as Country, COUNT(DISTINCT r.patent_id) AS total_patents
    FROM inventors i JOIN relationships r ON i.inventor_id = r.inventor_id
    WHERE i.country IS NOT NULL
    GROUP BY i.country ORDER BY total_patents DESC LIMIT 10;
    """
    df_cntry = pd.read_sql_query(q_cntry, conn)
    
    # Global metrics
    total_patents = pd.read_sql_query("SELECT COUNT(*) as c FROM patents", conn).iloc[0]['c']
    total_inventors = pd.read_sql_query("SELECT COUNT(*) as c FROM inventors", conn).iloc[0]['c']
    total_companies = pd.read_sql_query("SELECT COUNT(*) as c FROM companies", conn).iloc[0]['c']
    
    conn.close()
    return df_patents, df_inv, df_comp, df_cntry, total_patents, total_inventors, total_companies

try:
    df_patents, df_inv, df_comp, df_cntry, tot_p, tot_i, tot_c = load_data()
    
    # High-level metrics
    st.markdown("### Executive Summary")
    colA, colB, colC = st.columns(3)
    with colA:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{tot_p:,}</div><div class="metric-label">Total Patents Analyzed</div></div>', unsafe_allow_html=True)
    with colB:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{tot_i:,}</div><div class="metric-label">Unique Inventors</div></div>', unsafe_allow_html=True)
    with colC:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{tot_c:,}</div><div class="metric-label">Assignee Companies</div></div>', unsafe_allow_html=True)
        
    st.markdown("---")
    
    # Layout with columns for charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🏢 Top 10 Leading Companies")
        # Horizontal bar chart for companies to fix label overlapping
        chart_comp = alt.Chart(df_comp).mark_bar(cornerRadiusEnd=4, color='#4CAF50').encode(
            x=alt.X('total_patents:Q', title='Number of Patents'),
            y=alt.Y('Company:N', sort='-x', title='', axis=alt.Axis(labelLimit=250)),
            tooltip=['Company', 'total_patents']
        ).properties(height=350)
        st.altair_chart(chart_comp, use_container_width=True)

    with col2:
        st.subheader("🌎 Innovation by Country")
        # Horizontal bar chart for countries
        chart_cntry = alt.Chart(df_cntry).mark_bar(cornerRadiusEnd=4, color='#FF9800').encode(
            x=alt.X('total_patents:Q', title='Number of Patents'),
            y=alt.Y('Country:N', sort='-x', title=''),
            color=alt.Color('total_patents:Q', scale=alt.Scale(scheme='oranges'), legend=None),
            tooltip=['Country', 'total_patents']
        ).properties(height=350)
        st.altair_chart(chart_cntry, use_container_width=True)

    st.markdown("---")
    
    col3, col4 = st.columns([2, 1])
    
    with col3:
        st.subheader("📈 Patent Registration Trends Over Time")
        if not df_patents.empty:
            chart_trend = alt.Chart(df_patents).mark_area(
                line={'color':'#2196F3'},
                color=alt.Gradient(
                    gradient='linear',
                    stops=[alt.GradientStop(color='#2196F3', offset=0),
                           alt.GradientStop(color='rgba(255,255,255,0)', offset=1)],
                    x1=1, x2=1, y1=1, y2=0
                )
            ).encode(
                x=alt.X('year:O', title='Filing Year', axis=alt.Axis(labelAngle=-45)),
                y=alt.Y('total_patents:Q', title='Total Patents'),
                tooltip=['year', 'total_patents']
            ).properties(height=350)
            st.altair_chart(chart_trend, use_container_width=True)
        else:
            st.info("Insufficient historical date data to plot trends.")
            
    with col4:
        st.subheader("🧠 Top Inventors")
        st.dataframe(
            df_inv, 
            column_config={
                "total_patents": st.column_config.ProgressColumn("Patents Granted", format="%d", min_value=0, max_value=int(df_inv['total_patents'].max())),
            },
            hide_index=True,
            use_container_width=True
        )
    
except Exception as e:
    st.error(f"Error loading data. Ensure the ETL pipeline (main.py) has been run first. Details: {str(e)}")
    
st.markdown("---")
st.markdown("<p style='text-align: center; color: #888;'>Powered by Streamlit, Altair, Pandas, and SQLite</p>", unsafe_allow_html=True)
