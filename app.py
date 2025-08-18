# ------------------ Imports ------------------
import os
from pathlib import Path
from datetime import datetime
import pandas as pd
import streamlit as st
import altair as alt

# ------------------ Page Config ------------------
st.set_page_config(
    page_title="Visitor Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ------------------ Theme (light & dark) ------------------
THEMES = {
    "light": {
        "bg": "#f8fafc", "fg": "#111827", "card": "#ffffff",
        "muted": "#6b7280", "border": "#e5e7eb", "accent": "#2563eb",
        "shadow": "0 2px 6px rgba(0,0,0,.08)"
    },
    "dark": {
        "bg": "#0b1020", "fg": "#e8ebff", "card": "#151b31",
        "muted": "rgba(232,235,255,.75)", "border": "rgba(90,215,255,.18)", "accent": "#5ad7ff",
        "shadow": "0 8px 20px rgba(0,0,0,.35)"
    }
}
if "theme" not in st.session_state:
    st.session_state.theme = "light"

# ------------------ Data Loader ------------------
@st.cache_data(show_spinner=True)
def load_data(path: str, version: str = "") -> pd.DataFrame:
    def _read(p):
        df_ = pd.read_csv(p)
        if "event_time" not in df_.columns:
            raise ValueError("CSV must contain an 'event_time' column")
        df_["event_time"] = pd.to_datetime(df_["event_time"], errors="coerce")
        df_ = df_.dropna(subset=["event_time"])
        df_["date"] = df_["event_time"].dt.normalize()
        df_["hour"] = df_["event_time"].dt.hour
        df_["weekday"] = df_["event_time"].dt.day_name()
        return df_

    if path != "__parts__" and Path(path).exists():
        return _read(path)
    parts = sorted(Path("data/parts").glob("visitor_events_100k_part*.csv"))
    if not parts:
        st.stop()
    return pd.concat([_read(p) for p in parts], ignore_index=True)

# ------------------ Sidebar: Theme toggle + Filters ------------------
DATA_PATH_DEFAULT = "data/visitor_events_100k.csv"
with st.sidebar:
    st.header("Filters")

    st.session_state.theme = (
        "dark" if st.toggle("🌗 Dark mode", value=(st.session_state.theme == "dark"))
        else "light"
    )
    T = THEMES[st.session_state.theme]

    data_path = st.text_input("CSV path", DATA_PATH_DEFAULT)
    if Path(data_path).exists():
        version = str(Path(data_path).stat().st_mtime)
        df = load_data(data_path, version)
    else:
        parts = sorted(Path("data/parts").glob("visitor_events_100k_part*.csv"))
        version = "|".join(f"{p.name}:{p.stat().st_mtime}" for p in parts)
        df = load_data("__parts__", version)

    min_date, max_date = df["date"].min(), df["date"].max()
    date_range = st.date_input(
        "Date range", value=(min_date, max_date),
        min_value=min_date, max_value=max_date
    )

    def opts(col):
        return sorted(df[col].dropna().unique().tolist()) if col in df.columns else []

    os_sel   = st.multiselect("Device OS", opts("device_os"))
    cat_sel  = st.multiselect("Category",  opts("category"))
    evt_sel  = st.multiselect("Event type", opts("event_type") or opts("event"))
    country  = st.multiselect("Country",   opts("country"))
    search_sku = st.text_input("SKU contains…", "")

# ------------------ Themed CSS (no printed text) ------------------
st.markdown(f"""
<style>
:root {{
  --bg:{T['bg']}; --fg:{T['fg']}; --card:{T['card']};
  --muted:{T['muted']}; --border:{T['border']};
  --accent:{T['accent']}; --shadow:{T['shadow']};
}}
html, body, [data-testid="stAppViewContainer"] {{ background:var(--bg); color:var(--fg); }}
.block-container {{ max-width:1400px; padding-top:.5rem; }}

/* Sidebar */
[data-testid="stSidebar"] {{ background:var(--card); border-right:1px solid var(--border); }}
[data-testid="stSidebar"] * {{ color:var(--fg) !important; }}

/* Header */
.app-header {{
  position:sticky; top:0; z-index:20;
  display:flex; align-items:center; justify-content:space-between;
  background:var(--bg); padding:10px 6px 6px 4px; margin-bottom:6px;
}}
.app-header .left {{ display:flex; gap:12px; align-items:center; }}
.app-header .logo {{ font-size:28px; line-height:1; }}
.app-header h1 {{ margin:0; font-size:34px; color:var(--fg); letter-spacing:.2px; }}
.app-header p {{ margin:0; color:var(--muted); }}
.badge {{
  border:1px solid var(--border); background:var(--card); color:var(--fg);
  padding:6px 10px; border-radius:999px; font-size:.9rem; box-shadow:var(--shadow);
}}
.sep {{ border:none; border-top:1px solid var(--border); margin:10px 0 18px; }}

/* Metric cards */
div[data-testid="stMetric"] {{
  background:var(--card); border:1px solid var(--border);
  border-radius:12px; padding:14px 16px; box-shadow:var(--shadow);
}}
div[data-testid="stMetric"] [data-testid="stMetricLabel"] {{ color:var(--muted); font-weight:600; }}
div[data-testid="stMetric"] [data-testid="stMetricValue"] {{ font-size:2rem; color:var(--fg); }}

/* Inputs */
.stSelectbox, .stMultiSelect, .stTextInput, .stDateInput, .stTextInput input {{
  background:var(--card) !important; color:var(--fg) !important;
  border-radius:10px !important; border:1px solid var(--border) !important;
}}
.stSlider > div > div > div > div {{ background:var(--accent) !important; }}
</style>
""", unsafe_allow_html=True)

# ------------------ Header Component ------------------
def render_header(title: str, subtitle: str, date_range_text: str = ""):
    st.markdown(
        f"""
        <div class="app-header">
          <div class="left">
            <span class="logo">📊</span>
            <div>
              <h1>{title}</h1>
              <p>{subtitle}</p>
            </div>
          </div>
          <div class="right"><span class="badge">{date_range_text}</span></div>
        </div>
        <hr class="sep"/>
        """,
        unsafe_allow_html=True
    )

# ------------------ Filters → Mask ------------------
ev_col = "event_type" if "event_type" in df.columns else ("event" if "event" in df.columns else None)
mask = (df["date"] >= pd.to_datetime(date_range[0])) & (df["date"] <= pd.to_datetime(date_range[1]))
if os_sel and "device_os" in df.columns: mask &= df["device_os"].isin(os_sel)
if cat_sel and "category" in df.columns: mask &= df["category"].isin(cat_sel)
if evt_sel and ev_col:                   mask &= df[ev_col].isin(evt_sel)
if country and "country" in df.columns:  mask &= df["country"].isin(country)
if search_sku.strip() and "sku" in df.columns:
    mask &= df["sku"].str.contains(search_sku.strip(), case=False, na=False)
fdf = df.loc[mask].copy()

# ------------------ Header (now that date is known) ------------------
date_range_text = f"{date_range[0].strftime('%Y-%m-%d')} — {date_range[1].strftime('%Y-%m-%d')}"
render_header("Visitor Analytics Dashboard", "Events, users, conversions & revenue", date_range_text)

# ------------------ KPI Metrics ------------------
def nunique_safe(df_, *cols):
    for c in cols:
        if c in df_.columns:
            return df_[c].nunique()
    return 0

total_events = len(fdf)
unique_users = nunique_safe(fdf, "user_id", "userId")
purchases = int((fdf[ev_col] == "purchase").sum()) if ev_col else 0
revenue = float(fdf["revenue"].sum()) if "revenue" in fdf.columns else 0.0
views_clicks = int(fdf[ev_col].isin(["view", "click", "add_to_cart"]).sum()) if ev_col else 0
conv_rate = (purchases / views_clicks * 100) if views_clicks else 0.0

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total events", f"{total_events:,}")
c2.metric("Unique users", f"{unique_users:,}")
c3.metric("Purchases", f"{purchases:,}")
c4.metric("Revenue", f"₹{revenue:,.0f}")

st.divider()

# ------------------ Charts ------------------
left, right = st.columns([2, 1])

with left:
    ts = fdf.groupby("date")[ev_col].count().reset_index(name="events") if ev_col else \
         fdf.groupby("date").size().reset_index(name="events")
    chart = alt.Chart(ts).mark_line(point=True).encode(
        x=alt.X("date:T", title="Date"),
        y=alt.Y("events:Q", title="Events"),
        tooltip=["date:T", "events:Q"]
    ).properties(height=280, title="Events per day").configure_view(strokeWidth=0)
    st.altair_chart(chart, use_container_width=True)

    heat_src = fdf if ev_col else fdf.assign(event_type="event")
    heat = heat_src.groupby(["weekday","hour"])[ev_col or "event_type"].count() \
                   .reset_index(name="events")
    weekday_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    heat["weekday"] = pd.Categorical(heat["weekday"], categories=weekday_order, ordered=True)
    heat_chart = alt.Chart(heat).mark_rect().encode(
        x=alt.X("hour:O", title="Hour of day"),
        y=alt.Y("weekday:O", title="Weekday"),
        color=alt.Color("events:Q", title="Events"),
        tooltip=["weekday","hour","events"]
    ).properties(height=280, title="Traffic heatmap").configure_view(strokeWidth=0)
    st.altair_chart(heat_chart, use_container_width=True)

with right:
    if "category" in fdf.columns:
        top_cat = fdf.groupby("category")[ev_col or "date"].count() \
                     .reset_index(name="events").sort_values("events", ascending=False).head(10)
        cat_bar = alt.Chart(top_cat).mark_bar().encode(
            x=alt.X("events:Q", title="Events"),
            y=alt.Y("category:N", sort="-x", title="Category"),
            tooltip=["category","events"]
        ).properties(height=280, title="Top categories (by events)").configure_view(strokeWidth=0)
        st.altair_chart(cat_bar, use_container_width=True)

    if "sku" in fdf.columns:
        if "qty" in fdf.columns and ev_col:
            top_sku = fdf[fdf[ev_col] == "purchase"].groupby("sku")["qty"].sum() \
                      .reset_index().sort_values("qty", ascending=False).head(10)
            x_field, x_title = "qty:Q", "Units"
        else:
            top_sku = fdf.groupby("sku")[ev_col or "date"].count() \
                         .reset_index(name="events").sort_values("events", ascending=False).head(10)
            x_field, x_title = "events:Q", "Events"
        sku_bar = alt.Chart(top_sku).mark_bar().encode(
            x=alt.X(x_field, title=x_title),
            y=alt.Y("sku:N", sort="-x", title="SKU"),
            tooltip=list(top_sku.columns)
        ).properties(height=280, title="Top SKUs").configure_view(strokeWidth=0)
        st.altair_chart(sku_bar, use_container_width=True)

st.divider()
st.subheader("Filtered rows")
st.dataframe(fdf.head(1000), use_container_width=True, height=360)
st.download_button(
    "Download filtered CSV",
    data=fdf.to_csv(index=False).encode("utf-8"),
    file_name="filtered_events.csv",
    mime="text/csv",
)
st.caption("Provide a single CSV at data/visitor_events_100k.csv or parts in data/parts/visitor_events_100k_part*.csv")
