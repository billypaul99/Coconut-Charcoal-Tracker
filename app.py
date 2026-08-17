import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="Charcoal Tracker", page_icon="🥥", layout="wide"
)

# Custom mobile styling
st.markdown(
    """
    <style>
        .block-container { padding: 0.75rem 1rem 2rem 1rem; }
        .metric-card {
            background-color: #1e293b;
            border-radius: 12px;
            padding: 12px;
            border: 1px solid #334155;
            margin-bottom: 8px;
        }
        .metric-label { font-size: 0.8rem; color: #94a3b8; margin-bottom: 2px; }
        .metric-value { font-size: 1.3rem; font-weight: 700; color: #f8fafc; }
        .metric-delta { font-size: 0.75rem; font-weight: 600; }
        .delta-pos { color: #10b981; }
        .delta-neg { color: #ef4444; }
    </style>
""",
    unsafe_allow_html=True,
)


@st.cache_data
def load_data():
  df = pd.read_csv("icc_coconut_shell_charcoal_weekly_2021_2026.csv")
  df["report_date"] = pd.to_datetime(df["report_date"])
  return df.sort_values("report_date")


df = load_data()
latest = df.iloc[-1]
prev = df.iloc[-2]

st.title("🥥 Charcoal Pricing")
st.caption(
    f"ICC Benchmark | Week {int(latest['iso_week'])}, {int(latest['year'])}"
)

# Mobile KPI Cards
c1, c2 = st.columns(2)
with c1:
  wow_bm = (
      (latest["composite_benchmark_usd_mt"] - prev["composite_benchmark_usd_mt"])
      / prev["composite_benchmark_usd_mt"]
  ) * 100
  st.markdown(
      f"""
    <div class="metric-card">
        <div class="metric-label">Composite FOB</div>
        <div class="metric-value">${latest['composite_benchmark_usd_mt']:,.0f} <span style="font-size:0.75rem;">/MT</span></div>
        <div class="metric-delta {'delta-pos' if wow_bm >= 0 else 'delta-neg'}">
            {'+' if wow_bm >= 0 else ''}{wow_bm:.1f}% WoW
        </div>
    </div>
    """,
      unsafe_allow_html=True,
  )

with c2:
  wow_id = (
      (latest["indonesia_fob_usd_mt"] - prev["indonesia_fob_usd_mt"])
      / prev["indonesia_fob_usd_mt"]
  ) * 100
  st.markdown(
      f"""
    <div class="metric-card">
        <div class="metric-label">🇮🇩 Indonesia FOB</div>
        <div class="metric-value">${latest['indonesia_fob_usd_mt']:,.0f} <span style="font-size:0.75rem;">/MT</span></div>
        <div class="metric-delta {'delta-pos' if wow_id >= 0 else 'delta-neg'}">
            {'+' if wow_id >= 0 else ''}{wow_id:.1f}% WoW
        </div>
    </div>
    """,
      unsafe_allow_html=True,
  )

c3, c4 = st.columns(2)
with c3:
  wow_lk = (
      (latest["sri_lanka_fob_usd_mt"] - prev["sri_lanka_fob_usd_mt"])
      / prev["sri_lanka_fob_usd_mt"]
  ) * 100
  st.markdown(
      f"""
    <div class="metric-card">
        <div class="metric-label">🇱🇰 Sri Lanka FOB</div>
        <div class="metric-value">${latest['sri_lanka_fob_usd_mt']:,.0f} <span style="font-size:0.75rem;">/MT</span></div>
        <div class="metric-delta {'delta-pos' if wow_lk >= 0 else 'delta-neg'}">
            {'+' if wow_lk >= 0 else ''}{wow_lk:.1f}% WoW
        </div>
    </div>
    """,
      unsafe_allow_html=True,
  )

with c4:
  wow_in = (
      (latest["india_fob_usd_mt"] - prev["india_fob_usd_mt"])
      / prev["india_fob_usd_mt"]
  ) * 100
  st.markdown(
      f"""
    <div class="metric-card">
        <div class="metric-label">🇮🇳 India FOB</div>
        <div class="metric-value">${latest['india_fob_usd_mt']:,.0f} <span style="font-size:0.75rem;">/MT</span></div>
        <div class="metric-delta {'delta-pos' if wow_in >= 0 else 'delta-neg'}">
            {'+' if wow_in >= 0 else ''}{wow_in:.1f}% WoW
        </div>
    </div>
    """,
      unsafe_allow_html=True,
  )

# Chart Range Controls
st.markdown("---")
tf_col, metric_col = st.columns(2)
with tf_col:
  timeframe = st.selectbox(
      "Window", ["6M", "1Y", "3Y", "5Y", "ALL"], index=1, label_visibility="collapsed"
  )
with metric_col:
  view = st.selectbox(
      "Metric",
      ["FOB (USD/MT)", "Spreads vs Indonesia", "Domestic Local CCY"],
      index=0,
      label_visibility="collapsed",
  )

cutoff_days = {
    "6M": pd.DateOffset(months=6),
    "1Y": pd.DateOffset(years=1),
    "3Y": pd.DateOffset(years=3),
    "5Y": pd.DateOffset(years=5),
}
chart_df = (
    df[df["report_date"] >= (df["report_date"].max() - cutoff_days[timeframe])]
    if timeframe != "ALL"
    else df
)

# Plotly Interactive Chart
fig = go.Figure()
if view == "FOB (USD/MT)":
  fig.add_trace(
      go.Scatter(
          x=chart_df["report_date"],
          y=chart_df["sri_lanka_fob_usd_mt"],
          name="Sri Lanka",
          line=dict(color="#f59e0b", width=2.5),
      )
  )
  fig.add_trace(
      go.Scatter(
          x=chart_df["report_date"],
          y=chart_df["indonesia_fob_usd_mt"],
          name="Indonesia",
          line=dict(color="#3b82f6", width=2.5),
      )
  )
  fig.add_trace(
      go.Scatter(
          x=chart_df["report_date"],
          y=chart_df["india_fob_usd_mt"],
          name="India",
          line=dict(color="#10b981", width=2.5),
      )
  )
elif view == "Spreads vs Indonesia":
  fig.add_trace(
      go.Scatter(
          x=chart_df["report_date"],
          y=chart_df["spread_sri_lanka_vs_indonesia_usd"],
          name="LK Premium (+)",
          line=dict(color="#f59e0b", width=2),
      )
  )
  fig.add_trace(
      go.Scatter(
          x=chart_df["report_date"],
          y=chart_df["spread_india_vs_indonesia_usd"],
          name="IN Discount (-)",
          line=dict(color="#10b981", width=2),
      )
  )
  fig.add_hline(y=0, line_dash="dash", line_color="#64748b")
else:
  fig.add_trace(
      go.Scatter(
          x=chart_df["report_date"],
          y=chart_df["indonesia_domestic_idr_kg"],
          name="IDR/kg (ID)",
          line=dict(color="#3b82f6", width=2),
      )
  )

fig.update_layout(
    margin=dict(l=10, r=10, t=10, b=10),
    height=320,
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1,
        font=dict(size=10),
    ),
    xaxis=dict(showgrid=True, gridcolor="#334155", tickfont=dict(size=9)),
    yaxis=dict(showgrid=True, gridcolor="#334155", tickfont=dict(size=9)),
    hovermode="x unified",
)
st.plotly_chart(fig, use_container_width=True)
