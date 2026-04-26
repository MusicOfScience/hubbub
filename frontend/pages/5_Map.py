"""Map page — booth-level geographic visualisation."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pandas as pd
import streamlit as st

try:
    import folium
    from streamlit_folium import st_folium
    FOLIUM_AVAILABLE = True
except ImportError:
    FOLIUM_AVAILABLE = False

st.set_page_config(page_title="Map — MOE", page_icon="🗺️", layout="wide")

css_path = Path(__file__).parent.parent / "styles" / "custom.css"
if css_path.exists():
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.title("🗺️ Booth Map")

if not FOLIUM_AVAILABLE:
    st.error("folium and streamlit-folium are required for this page. Install with: pip install folium streamlit-folium")
    st.stop()

booths = st.session_state.get("booths", [])
live_df: pd.DataFrame = st.session_state.get("live_count", pd.DataFrame())
election = st.session_state.get("election")

# ── Build booth data ──────────────────────────────────────────────────────────
if not booths:
    st.info("No booth data loaded. Map requires booth coordinates.")
    st.stop()

booth_df = pd.DataFrame([
    {"booth_id": b.booth_id, "booth_name": b.name, "lat": b.lat, "lon": b.lon, "enrolled": b.enrolled}
    for b in booths
])

# Merge with live data
if live_df is not None and not live_df.empty:
    tcp_cols = [c for c in live_df.columns if "_tcp" in c]
    if len(tcp_cols) >= 2:
        live_agg = live_df[["booth_id", tcp_cols[0], tcp_cols[1]]].copy()
        live_agg["tcp_margin"] = live_agg[tcp_cols[0]] - live_agg[tcp_cols[1]]
        live_agg["tcp_total"] = live_agg[tcp_cols[0]] + live_agg[tcp_cols[1]]
        live_agg["alp_tcp_pct"] = live_agg.apply(
            lambda r: r[tcp_cols[0]] / r["tcp_total"] * 100 if r["tcp_total"] > 0 else 50, axis=1
        )
        booth_df = booth_df.merge(live_agg[["booth_id", "tcp_margin", "alp_tcp_pct"]], on="booth_id", how="left")
    else:
        booth_df["tcp_margin"] = 0
        booth_df["alp_tcp_pct"] = 50.0
else:
    booth_df["tcp_margin"] = 0
    booth_df["alp_tcp_pct"] = 50.0

booth_df["tcp_margin"] = booth_df["tcp_margin"].fillna(0)
booth_df["alp_tcp_pct"] = booth_df["alp_tcp_pct"].fillna(50.0)

# ── Map controls ──────────────────────────────────────────────────────────────
col_ctrl1, col_ctrl2 = st.columns([3, 1])
with col_ctrl2:
    show_swing = st.toggle("Show Swing Layer", value=False)
    map_zoom = st.slider("Zoom", 10, 16, 13)

# ── Build Folium map ──────────────────────────────────────────────────────────
centre_lat = booth_df["lat"].mean()
centre_lon = booth_df["lon"].mean()

m = folium.Map(location=[centre_lat, centre_lon], zoom_start=map_zoom, tiles="CartoDB positron")

# Add booth markers
for _, row in booth_df.iterrows():
    pct = row["alp_tcp_pct"]
    margin = row["tcp_margin"]

    # Colour gradient: deep red (ALP) to deep blue (LIB)
    if pct >= 55:
        colour = "#E53935"
    elif pct >= 52:
        colour = "#EF9A9A"
    elif pct >= 50:
        colour = "#FFCDD2"
    elif pct >= 48:
        colour = "#BBDEFB"
    elif pct >= 45:
        colour = "#64B5F6"
    else:
        colour = "#1565C0"

    popup_html = f"""
    <b>{row['booth_name']}</b><br>
    Enrolled: {row['enrolled']:,}<br>
    ALP TCP: {pct:.1f}%<br>
    Margin: {int(margin):+,}
    """
    folium.CircleMarker(
        location=[row["lat"], row["lon"]],
        radius=8,
        color="#333",
        weight=1,
        fill=True,
        fill_color=colour,
        fill_opacity=0.85,
        popup=folium.Popup(popup_html, max_width=200),
        tooltip=f"{row['booth_name']}: {pct:.1f}% ALP",
    ).add_to(m)

# GeoJSON uploader
st.markdown("---")
uploaded_geojson = st.file_uploader("Upload Electorate Boundary (GeoJSON)", type=["geojson", "json"])
if uploaded_geojson:
    import json
    geojson_data = json.load(uploaded_geojson)
    folium.GeoJson(
        geojson_data,
        name="Electorate Boundary",
        style_function=lambda x: {"fillColor": "transparent", "color": "#333", "weight": 2},
    ).add_to(m)
    folium.LayerControl().add_to(m)

# ── Render map ────────────────────────────────────────────────────────────────
with col_ctrl1:
    st_folium(m, width=900, height=550, returned_objects=[])

# ── Legend ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("**Legend:**")
legend_cols = st.columns(6)
legend_items = [
    ("#E53935", "ALP >55%"), ("#EF9A9A", "ALP 52-55%"),
    ("#FFCDD2", "ALP 50-52%"), ("#BBDEFB", "LIB 50-52%"),
    ("#64B5F6", "LIB 52-55%"), ("#1565C0", "LIB >55%"),
]
for col, (colour, label) in zip(legend_cols, legend_items):
    col.markdown(
        f'<span style="background:{colour};padding:4px 10px;border-radius:4px;color:#333;font-size:0.8rem">{label}</span>',
        unsafe_allow_html=True,
    )
