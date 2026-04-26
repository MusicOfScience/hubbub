"""Commentary page — timeline of commentary entries."""
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pandas as pd
import streamlit as st

from frontend.components.ticker import get_ticker_messages

st.set_page_config(page_title="Commentary — MOE", page_icon="📝", layout="wide")

css_path = Path(__file__).parent.parent / "styles" / "custom.css"
if css_path.exists():
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.title("📝 Commentary")

if "commentary" not in st.session_state:
    st.session_state["commentary"] = []

CATEGORIES = ["General", "TCP Update", "Swing Analysis", "Preference Flow", "Booth Report", "Declaration Votes", "Call/Projection"]

# ── Add entry ─────────────────────────────────────────────────────────────────
st.markdown("### Add Commentary Entry")
with st.form("commentary_form"):
    col_c1, col_c2 = st.columns([2, 1])
    with col_c1:
        text = st.text_area("Commentary", placeholder="Enter commentary text here...", height=100)
    with col_c2:
        author = st.text_input("Author", value="Analyst")
        category = st.selectbox("Category", CATEGORIES)
        use_now = st.checkbox("Use current time", value=True)
        manual_time = st.time_input("Or set time manually", value=datetime.now().time()) if not use_now else None

    submitted = st.form_submit_button("➕ Add Entry", type="primary")
    if submitted:
        if text.strip():
            ts = datetime.now().strftime("%H:%M:%S") if use_now else str(manual_time)
            st.session_state["commentary"].append({
                "timestamp": datetime.now().strftime("%Y-%m-%d") + " " + ts,
                "author": author,
                "category": category,
                "text": text,
            })
            st.success("Commentary added.")
        else:
            st.warning("Commentary text cannot be empty.")

# ── Category filter ───────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### Commentary Timeline")
all_entries = st.session_state.get("commentary", [])

cat_filter = st.multiselect("Filter by Category", CATEGORIES, default=CATEGORIES)
filtered = [e for e in all_entries if e["category"] in cat_filter]

if filtered:
    cat_colours = {
        "General": "#555", "TCP Update": "#E53935", "Swing Analysis": "#1565C0",
        "Preference Flow": "#2E7D32", "Booth Report": "#E65100",
        "Declaration Votes": "#6A1B9A", "Call/Projection": "#C62828",
    }
    for entry in reversed(filtered):
        colour = cat_colours.get(entry["category"], "#555")
        st.markdown(
            f"""
            <div class="card" style="border-left:4px solid {colour}">
              <div style="font-size:0.8rem;color:#888;margin-bottom:4px">
                🕐 {entry['timestamp']} &nbsp;|&nbsp;
                <strong style="color:{colour}">{entry['category']}</strong> &nbsp;|&nbsp;
                ✍️ {entry['author']}
              </div>
              <div>{entry['text']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
else:
    st.info("No commentary entries yet.")

# ── Ticker preview ────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### Ticker Preview")
ticker_data = {
    "election": st.session_state.get("election"),
    "live_count": st.session_state.get("live_count"),
}
ticker_msgs = get_ticker_messages(ticker_data)
if all_entries:
    latest = all_entries[-1]
    ticker_msgs.insert(0, f"📝 {latest['category']}: {latest['text'][:60]}{'...' if len(latest['text']) > 60 else ''}")

st.info("  •  ".join(ticker_msgs))

# ── Export ────────────────────────────────────────────────────────────────────
st.markdown("---")
if all_entries:
    export_df = pd.DataFrame(all_entries)
    csv_bytes = export_df.to_csv(index=False).encode()
    st.download_button(
        label="⬇️ Export Commentary CSV",
        data=csv_bytes,
        file_name="commentary_export.csv",
        mime="text/csv",
    )
