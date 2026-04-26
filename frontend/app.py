"""Margin of Error — Main Streamlit App Entry Point."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
from backend.config import DATA_DIR
from backend.ingestion.aec_loader import load_election_config
from backend.ingestion.csv_loader import (
    load_candidates,
    load_booths,
    load_live_count,
    load_declaration_votes,
    load_historical_booths,
)
from backend.utils.helpers import load_json
from frontend.components.ticker import render_ticker, get_ticker_messages

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Margin of Error",
    page_icon="🗳️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Load custom CSS ───────────────────────────────────────────────────────────
css_path = Path(__file__).parent / "styles" / "custom.css"
if css_path.exists():
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def _load_all_data():
    """Load all sample data into session state (called once)."""
    try:
        election = load_election_config(str(DATA_DIR / "election_config.json"))
        st.session_state["election"] = election
    except Exception as e:
        st.session_state["election"] = None
        st.session_state["load_error"] = str(e)

    st.session_state["candidates"] = load_candidates(str(DATA_DIR / "candidates.csv"))
    st.session_state["booths"] = load_booths(str(DATA_DIR / "booths.csv"))
    st.session_state["live_count"] = load_live_count(str(DATA_DIR / "live_count.csv"))
    st.session_state["declaration_votes"] = load_declaration_votes(str(DATA_DIR / "declaration_votes.csv"))
    st.session_state["historical_booths"] = load_historical_booths(str(DATA_DIR / "historical_booths.csv"))

    try:
        scenario = load_json(str(DATA_DIR / "scenario_default.json"))
        st.session_state["scenario"] = scenario
    except Exception:
        st.session_state["scenario"] = {}

    st.session_state["polls"] = []
    st.session_state["commentary"] = []
    st.session_state["intelligence"] = []
    st.session_state["data_loaded"] = True


# ── Bootstrap data ────────────────────────────────────────────────────────────
if not st.session_state.get("data_loaded"):
    _load_all_data()

election = st.session_state.get("election")

# ── Ticker ────────────────────────────────────────────────────────────────────
ticker_data = {
    "election": election,
    "live_count": st.session_state.get("live_count"),
}
ticker_messages = get_ticker_messages(ticker_data)
render_ticker(ticker_messages)

# ── Main heading ──────────────────────────────────────────────────────────────
st.title("🗳️ Margin of Error")
st.caption("Australian Election Prediction & Live-Count Analysis")

# ── Contest selector ─────────────────────────────────────────────────────────
contest_options = ["Banksia 2026"]
selected = st.selectbox("📍 Contest", contest_options, index=0)

# ── Info columns ─────────────────────────────────────────────────────────────
if election:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Electorate", election.electorate)
    col2.metric("State", election.state)
    col3.metric("Enrolled Voters", f"{election.enrolled_voters:,}")
    col4.metric("Election Date", election.election_date)

    st.markdown("---")
    st.markdown("### Navigate the analysis using the pages in the sidebar:")
    col_a, col_b, col_c, col_d = st.columns(4)
    col_a.info("📊 **Live Count**\nReal-time TCP margin and count progress")
    col_b.info("🔮 **Prediction**\nMonte Carlo probability of victory")
    col_c.info("📐 **Swingometer**\nInteractive swing scenarios")
    col_d.info("🗺️ **Map**\nBooth-level geographic view")
else:
    st.warning("⚠️ Election data not loaded. Check your data directory configuration.")
    if st.button("🔄 Reload Data"):
        st.session_state["data_loaded"] = False
        st.rerun()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🗳️ Margin of Error")
    st.markdown("---")

    if election:
        st.markdown(f"**{election.electorate}**, {election.state}")
        st.markdown(f"📅 {election.election_date}")
        st.markdown(f"👥 {election.enrolled_voters:,} enrolled")
        st.markdown("---")
        st.markdown("**TCP Contest:**")
        for cid in election.tcp_candidates:
            candidate_info = next(
                (c for c in election.candidates if c["candidate_id"] == cid), {}
            )
            colour = candidate_info.get("colour", "#757575")
            name = candidate_info.get("name", cid)
            abbrev = candidate_info.get("party_abbrev", "")
            st.markdown(
                f'<span style="color:{colour}">⬤</span> **{name}** ({abbrev})',
                unsafe_allow_html=True
            )

    st.markdown("---")
    if st.button("🔄 Refresh Data"):
        st.session_state["data_loaded"] = False
        st.rerun()
    st.caption(f"Data dir: `{DATA_DIR}`")
