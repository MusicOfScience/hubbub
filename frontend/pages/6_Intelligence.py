"""Intelligence page — data uploads and notes."""
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Intelligence — MOE", page_icon="🔍", layout="wide")

css_path = Path(__file__).parent.parent / "styles" / "custom.css"
if css_path.exists():
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.title("🔍 Intelligence")

if "intelligence" not in st.session_state:
    st.session_state["intelligence"] = []

# ── File uploader ─────────────────────────────────────────────────────────────
st.markdown("### Upload Data")
uploaded_file = st.file_uploader("Upload CSV or XLSX", type=["csv", "xlsx"])

uploaded_df = None
if uploaded_file:
    try:
        if uploaded_file.name.endswith(".csv"):
            uploaded_df = pd.read_csv(uploaded_file)
        else:
            uploaded_df = pd.read_excel(uploaded_file)
        st.success(f"Loaded {len(uploaded_df):,} rows × {len(uploaded_df.columns)} columns")
    except Exception as e:
        st.error(f"Error reading file: {e}")

if uploaded_df is not None:
    st.markdown("---")
    st.markdown("### Uploaded Data")

    # Search
    search = st.text_input("🔍 Search", placeholder="Filter rows...")
    display_df = uploaded_df.copy()
    if search:
        mask = display_df.astype(str).apply(lambda col: col.str.contains(search, case=False)).any(axis=1)
        display_df = display_df[mask]

    st.dataframe(display_df, use_container_width=True, hide_index=True)

# ── Manual entry form ──────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### Manual Intelligence Entry")

TAGS = ["Polling", "Field Report", "Media", "Demographic", "Booth Data", "Other"]

with st.form("intel_entry_form"):
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        source = st.text_input("Source", placeholder="e.g. Campaign contact")
        tag = st.selectbox("Category/Tag", TAGS)
        confidence = st.select_slider("Confidence", options=["Low", "Medium", "High", "Verified"], value="Medium")
    with col_f2:
        note = st.text_area("Note", placeholder="Enter intelligence note here...", height=100)

    submitted = st.form_submit_button("➕ Add Entry", type="primary")
    if submitted:
        if note.strip():
            st.session_state["intelligence"].append({
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "source": source,
                "tag": tag,
                "confidence": confidence,
                "note": note,
            })
            st.success("Entry added.")
        else:
            st.warning("Note cannot be empty.")

# ── Display entries ────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### Intelligence Log")
entries = st.session_state.get("intelligence", [])
if entries:
    tag_filter = st.multiselect("Filter by Tag", TAGS, default=TAGS)
    filtered = [e for e in entries if e["tag"] in tag_filter]

    for entry in reversed(filtered):
        conf_colour = {"Low": "#E65100", "Medium": "#1565C0", "High": "#2E7D32", "Verified": "#6A1B9A"}.get(entry["confidence"], "#555")
        st.markdown(
            f"""
            <div class="card">
              <div class="card-title">{entry['tag']} — {entry['source']}</div>
              <div>{entry['note']}</div>
              <div style="margin-top:6px;font-size:0.8rem;color:#888">
                🕐 {entry['timestamp']} &nbsp;|&nbsp;
                <span style="color:{conf_colour}">● {entry['confidence']}</span>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
else:
    st.info("No intelligence entries yet.")
