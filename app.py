import os
from pathlib import Path
import pandas as pd
import streamlit as st
import altair as alt

import streamlit as st
from datetime import datetime

st.set_page_config(page_title="Visitor Dashboard", layout="wide", initial_sidebar_state="expanded")

# ---------- Theme system (light & dark) ----------
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

with st.sidebar:
    st.header("Filters")
    st.session_state.theme = "dark" if st.toggle("🌗 Dark mode", value=(st.session_state.theme=="dark")) else "light"

T = THEMES[st.session_state.theme]

# ---------- Inject CSS using theme variables ----------
st.markdown(f"""
<style>
:root {{
  --bg: {T['bg']};
  --fg: {T['fg']};
  --card: {T['card']};
  --muted: {T['muted']};
  --border: {T['border']};
  --accent: {T['accent']};
  --shadow: {T['shadow']};
}}

html, body, [data-testid="stAppViewContainer"] {{
  background: var(--bg);
  color: var(--fg);
}}
.block-container {{ max-width: 1400px; padding-top: .5rem; }}

/* Sidebar */
[data-testid="stSidebar"] {{ background: var(--card); border-right: 1px solid var(--border); }}
[data-testid="stSidebar"] * {{ color: var(--fg) !important; }}

/* Header bar */
.app-header {{
  display:flex; align-items:center; justify-content:space-between;
  background: linear-gradient(180deg, rgba(0,0,0,0.0), rgba(0,0,0,0.0)), var(--bg);
  padding: 12px 8px 6px 4px; margin-bottom: 6px;
}}
.app-header .left {{ display:flex; gap:12px; align-items:center; }}
.app-header .logo {{ font-size: 28px; line-height: 1; }}
.app-header h1 {{ margin:0; font-size: 34px; color: var(--fg); letter-spacing:.2px; }}
.app-header p {{ margin:0; color: var(--muted); }}

.badge {{
  border:1px solid var(--border);
  background: var(--card);
  color: var(--fg);
  padding:6px 10px; border-radius: 999px; font-size:.9rem;
  box-shadow: var(--shadow);
}}

.sep {{ border:none; border-top:1px solid var(--border); margin:10px 0 18px; }}

/* Metric cards */
div[data-testid="stMetric"] {{
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 14px 16px;
  box-shadow: var(--shadow);
}}
div[data-testid="stMetric"] [data-testid="stMetricLabel"] {{ color: var(--muted); font-weight:600; }}
div[data-testid="stMetric"] [data-testid="stMetricValue"] {{ font-size: 2rem; color: var(--fg); }}

/* Inputs */
.stSelectbox, .stMultiSelect, .stTextInput, .stDateInput, .stTextInput input {{
  background: var(--card) !important; color: var(--fg) !important;
  border-radius: 10px !important; border: 1px solid var(--border) !important;
}}
.stSlider > div > div > div > div {{ background: var(--accent) !important; }}
</style>
""", unsafe_allow_html=True)

# ---------- Header component ----------
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
            <div class="right">
                <span class="badge">{date_range_text}</span>
            </div>
        </div>
        <hr class="sep"/>
        """,
        unsafe_allow_html=True
    )

# Example call (pass your actual selected date range later)
# render_header("Visitor Analytics Dashboard", "Events, users, conversions & revenue", "2024-01-01 — 2024-05-24")



# st.set_page_config(page_title="E-commerce Visitor Dashboard", page_icon="📊", layout="wide")

import streamlit as st

# st.set_page_config(page_title="Visitor Dashboard", layout="wide", initial_sidebar_state="expanded")

# ---- CSS (no raw text on page) ----
st.markdown("""
<style>
/* Tighten main container and spacing */
.block-container { max-width: 1400px; padding-top: 1rem; }

/* Sidebar look */
[data-testid="stSidebar"] {
  background: #101732;
  border-right: 1px solid rgba(255,255,255,0.06);
}
[data-testid="stSidebar"] * { color: #e8ebff !important; }

/* Headings */
h1, h2, h3 { color: #e8ebff; letter-spacing: .2px; }

/* Metric cards */
div[data-testid="stMetric"] {
  background: #151b31;
  border: 1px solid rgba(90,215,255,.18);
  border-radius: 14px;
  padding: 14px 16px;
  box-shadow: 0 8px 20px rgba(0,0,0,.25), inset 0 1px rgba(255,255,255,.04);
}
div[data-testid="stMetric"] [data-testid="stMetricLabel"] {
  color: rgba(232,235,255,.75);
  font-weight: 600;
}
div[data-testid="stMetric"] [data-testid="stMetricValue"] {
  font-size: 2.1rem;
}

/* Inputs */
.stSelectbox, .stMultiSelect, .stTextInput, .stDateInput, .stTextInput input {
  background: #151b31 !important;
  color: #e8ebff !important;
  border-radius: 10px !important;
  border: 1px solid rgba(90,215,255,.18) !important;
}

/* Charts spacing */
.element-container { margin-bottom: 1rem; }
hr { border-color: rgba(255,255,255,.08); }
</style>
""", unsafe_allow_html=True)


def inject_css(path="style.css"):
    if Path(path).exists():
        st.markdown(Path(path).read_text(), unsafe_allow_html=True)
inject_css()

# @st.cache_data(show_spinner=True)
# def load_data(path: str, version: str = "") -> pd.DataFrame:
#     if path != "__parts__" and Path(path).exists():
#         df = pd.read_csv(path, parse_dates=["event_time"])
#     else:
#         parts = sorted(Path("data/parts").glob("visitor_events_100k_part*.csv"))
#         if not parts:
#             st.stop()
#         dfs = [pd.read_csv(p, parse_dates=["event_time"]) for p in parts]
#         df = pd.concat(dfs, ignore_index=True)
#     df["date"] = df["event_time"].dt.date
#     df["hour"] = df["event_time"].dt.hour
#     df["weekday"] = df["event_time"].dt.day_name()
#     return df

@st.cache_data(show_spinner=True)
def load_data(path: str, version: str = "") -> pd.DataFrame:
    import pandas as pd
    from pathlib import Path

    def _read(p):
        # robust parse; if the column exists but isn't parsed, coerce it
        df_ = pd.read_csv(p)
        if "event_time" not in df_.columns:
            raise ValueError("CSV must contain an 'event_time' column")
        df_["event_time"] = pd.to_datetime(df_["event_time"], errors="coerce")
        df_ = df_.dropna(subset=["event_time"])  # drop bad rows if any
        # IMPORTANT: keep 'date' as datetime64[ns], not .dt.date
        df_["date"] = df_["event_time"].dt.normalize()      # 00:00 of each day
        df_["hour"] = df_["event_time"].dt.hour
        df_["weekday"] = df_["event_time"].dt.day_name()
        return df_

    if path != "__parts__" and Path(path).exists():
        df = _read(path)
    else:
        parts = sorted(Path("data/parts").glob("visitor_events_100k_part*.csv"))
        if not parts:
            st.stop()
        df = pd.concat([_read(p) for p in parts], ignore_index=True)
    return df

DATA_PATH_DEFAULT = "data/visitor_events_100k.csv"

with st.sidebar:
    st.header("Filters")
    data_path = st.text_input("CSV path", DATA_PATH_DEFAULT)
    if Path(data_path).exists():
        version = str(Path(data_path).stat().st_mtime)
        df = load_data(data_path, version)
    else:
        parts = sorted(Path("data/parts").glob("visitor_events_100k_part*.csv"))
        version = "|".join(f"{p.name}:{p.stat().st_mtime}" for p in parts)
        df = load_data("__parts__", version)

    min_date, max_date = df["date"].min(), df["date"].max()
    date_range = st.date_input("Date range", value=(min_date, max_date), min_value=min_date, max_value=max_date)
    os_sel   = st.multiselect("Device OS", sorted(df["device_os"].unique().tolist()))
    cat_sel  = st.multiselect("Category", sorted(df["category"].unique().tolist()))
    evt_sel  = st.multiselect("Event type", sorted(df["event_type"].unique().tolist()))
    country  = st.multiselect("Country", sorted(df["country"].unique().tolist()))
    search_sku = st.text_input("SKU contains…", "")

mask = (df["date"] >= pd.to_datetime(date_range[0])) & (df["date"] <= pd.to_datetime(date_range[1]))
if os_sel:  mask &= df["device_os"].isin(os_sel)
if cat_sel: mask &= df["category"].isin(cat_sel)
if evt_sel: mask &= df["event_type"].isin(evt_sel)
if country: mask &= df["country"].isin(country)
if search_sku.strip():
    mask &= df["sku"].str.contains(search_sku.strip(), case=False, na=False)
fdf = df.loc[mask].copy()

col1, col2, col3, col4 = st.columns(4)
total_events = len(fdf)
unique_users = fdf["user_id"].nunique()
purchases    = (fdf["event_type"] == "purchase").sum()
revenue      = float(fdf["revenue"].sum())
views_clicks = (fdf["event_type"].isin(["view","click","add_to_cart"])).sum()
conv_rate    = (purchases / views_clicks * 100) if views_clicks else 0.0
col1.metric("Total events", f"{total_events:,}")
col2.metric("Unique users", f"{unique_users:,}")
col3.metric("Purchases", f"{purchases:,}")
col4.metric("Revenue", f"₹{revenue:,.0f}")

st.divider()

left, right = st.columns([2, 1])
with left:
    ts = fdf.groupby("date")["event_type"].count().reset_index(name="events")
    chart = alt.Chart(ts).mark_line(point=True).encode(
        x=alt.X("date:T", title="Date"),
        y=alt.Y("events:Q", title="Events"),
        tooltip=["date:T", "events:Q"]
    ).properties(height=280, title="Events per day")
    st.altair_chart(chart, use_container_width=True)

    heat = fdf.groupby(["weekday","hour"])["event_type"].count().reset_index(name="events")
    weekday_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    heat["weekday"] = pd.Categorical(heat["weekday"], categories=weekday_order, ordered=True)
    heat_chart = alt.Chart(heat).mark_rect().encode(
        x=alt.X("hour:O", title="Hour of day"),
        y=alt.Y("weekday:O", title="Weekday"),
        color=alt.Color("events:Q", title="Events"),
        tooltip=["weekday","hour","events"]
    ).properties(height=280, title="Traffic heatmap")
    st.altair_chart(heat_chart, use_container_width=True)

with right:
    top_cat = fdf.groupby("category")["event_type"].count().reset_index(name="events").sort_values("events", ascending=False).head(10)
    cat_bar = alt.Chart(top_cat).mark_bar().encode(
        x=alt.X("events:Q", title="Events"),
        y=alt.Y("category:N", sort="-x", title="Category"),
        tooltip=["category","events"]
    ).properties(height=280, title="Top categories (by events)")
    st.altair_chart(cat_bar, use_container_width=True)

    top_sku = fdf[fdf["event_type"] == "purchase"].groupby("sku")["qty"].sum().reset_index().sort_values("qty", ascending=False).head(10)
    sku_bar = alt.Chart(top_sku).mark_bar().encode(
        x=alt.X("qty:Q", title="Units"),
        y=alt.Y("sku:N", sort="-x", title="SKU"),
        tooltip=["sku","qty"]
    ).properties(height=280, title="Top SKUs (purchased units)")
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
st.caption("Data can be provided as a single CSV at data/visitor_events_100k.csv or as parts in data/parts/visitor_events_100k_part*.csv")
