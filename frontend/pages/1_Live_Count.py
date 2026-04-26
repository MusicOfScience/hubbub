"""Live Count page — real-time TCP margin and count progress."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pandas as pd
import streamlit as st

from backend.analysis.live_count import (
    calculate_tcp_margin,
    calculate_count_progress,
    estimate_outstanding_votes,
    project_final_margin,
    recount_risk,
    count_status,
    required_vote_share,
)
from frontend.components.tables import render_vote_type_table

st.set_page_config(page_title="Live Count — MOE", page_icon="📊", layout="wide")

css_path = Path(__file__).parent.parent / "styles" / "custom.css"
if css_path.exists():
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.title("📊 Live Count")

live_df: pd.DataFrame = st.session_state.get("live_count", pd.DataFrame())
decl_df: pd.DataFrame = st.session_state.get("declaration_votes", pd.DataFrame())
election = st.session_state.get("election")

if live_df is None or (hasattr(live_df, "empty") and live_df.empty):
    st.info("No live count data loaded yet. Data will appear here once a count file is available.")
    st.stop()

# ── TCP Margin ────────────────────────────────────────────────────────────────
votes_margin, pct_margin = calculate_tcp_margin(live_df)
colour = "#E53935" if votes_margin > 0 else "#1565C0"
leader_id = ""
if election:
    tcp_cols = [c for c in live_df.columns if "_tcp" in c]
    if tcp_cols:
        leader_id = tcp_cols[0].replace("_tcp", "").replace("_", " ").title() if votes_margin > 0 else tcp_cols[1].replace("_tcp", "").replace("_", " ").title()

st.markdown("### Two-Candidate Preferred Margin")
col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    st.markdown(
        f'<div class="margin-display" style="color:{colour}">{votes_margin:+,} votes</div>',
        unsafe_allow_html=True,
    )
    st.caption(f"TCP margin: {pct_margin:+.2f} pp from 50%")
    if leader_id:
        st.caption(f"Leader: {leader_id}")

# ── Count Progress ────────────────────────────────────────────────────────────
primary_cols = [c for c in live_df.columns if "_primary" in c]
total_counted = int(live_df[primary_cols].sum().sum()) if primary_cols else 0

enrolled = int(live_df["total_enrolled"].sum()) if "total_enrolled" in live_df.columns else (
    election.enrolled_voters if election else 0
)
counted_pct = calculate_count_progress(total_counted, enrolled)
status = count_status(counted_pct)

status_colours = {
    "early": "#1565C0", "developing": "#E65100",
    "mature": "#2E7D32", "near-final": "#C62828"
}
status_colour = status_colours.get(status, "#555")

with col2:
    st.metric("Votes Counted", f"{total_counted:,}")
    st.metric("Total Enrolled", f"{enrolled:,}")
with col3:
    st.metric("Count Progress", f"{counted_pct:.1f}%")
    st.markdown(
        f'<span class="badge badge-{status.replace("-","")}" style="background:{status_colour}20;color:{status_colour}">{status.upper()}</span>',
        unsafe_allow_html=True,
    )

st.progress(counted_pct / 100)

# ── Recount Risk ──────────────────────────────────────────────────────────────
risk_level, threshold = recount_risk(votes_margin)
st.markdown("---")
col_r1, col_r2 = st.columns(2)
with col_r1:
    risk_colours = {"high": "#E53935", "moderate": "#E65100", "low": "#2E7D32"}
    rc = risk_colours.get(risk_level, "#555")
    st.markdown(
        f"**Recount Risk:** <span class='risk-{risk_level}'>{risk_level.upper()}</span>",
        unsafe_allow_html=True,
    )
    st.caption(f"Threshold: ±{threshold:,} votes")

# ── Vote Type Breakdown ───────────────────────────────────────────────────────
st.markdown("---")
st.subheader("Vote Type Breakdown")
if not decl_df.empty:
    render_vote_type_table(decl_df)
else:
    st.info("Declaration vote data not available.")

# ── Outstanding Votes Estimator ───────────────────────────────────────────────
st.markdown("---")
st.subheader("Outstanding Votes Estimator")
outstanding = estimate_outstanding_votes(decl_df, live_df)
if outstanding:
    ov_df = pd.DataFrame([
        {"Vote Type": k.replace("_", " ").title(), "Outstanding": v}
        for k, v in outstanding.items()
    ])
    col_ov1, col_ov2 = st.columns([1, 1])
    with col_ov1:
        st.dataframe(ov_df, use_container_width=True, hide_index=True)
    with col_ov2:
        total_outstanding = sum(outstanding.values())
        st.metric("Total Outstanding", f"{total_outstanding:,}")

    # Preference assumptions from scenario
    scenario = st.session_state.get("scenario", {})
    pref_assumptions = {
        "postal": scenario.get("postal_alp_lean", 46.0) / 100,
        "pre_poll": 0.52,
        "absent": 0.51,
        "provisional": 0.50,
    }
    projected_margin, (low, high) = project_final_margin(votes_margin, outstanding, pref_assumptions)

    st.markdown("**Projected Final Margin (based on current preferences)**")
    pm_colour = "#E53935" if projected_margin > 0 else "#1565C0"
    st.markdown(
        f'<span style="font-size:1.6rem;font-weight:700;color:{pm_colour}">{projected_margin:+,}</span> '
        f'<span style="color:#888"> (range: {low:+,} to {high:+,})</span>',
        unsafe_allow_html=True,
    )
else:
    st.info("Outstanding vote data not available.")

# ── Required Vote Share ───────────────────────────────────────────────────────
st.markdown("---")
st.subheader("Required Vote Share Calculator")
tcp_cols = [c for c in live_df.columns if "_tcp" in c]
if len(tcp_cols) >= 2 and outstanding:
    current_votes = {
        tcp_cols[0]: int(live_df[tcp_cols[0]].sum()),
        tcp_cols[1]: int(live_df[tcp_cols[1]].sum()),
    }
    req_share = required_vote_share(current_votes, outstanding)
    trailing_name = min(current_votes, key=current_votes.get).replace("_tcp", "").replace("_", " ").title()
    req_colour = "#E53935" if req_share > 55 else ("#E65100" if req_share > 52 else "#2E7D32")
    st.markdown(
        f"**{trailing_name}** needs "
        f'<span style="font-size:1.4rem;font-weight:700;color:{req_colour}">{req_share:.1f}%</span>'
        f" of outstanding votes to win.",
        unsafe_allow_html=True,
    )
else:
    st.info("Enter live count and outstanding data to calculate required vote share.")

# ── Booths Table ───────────────────────────────────────────────────────────────
st.markdown("---")
with st.expander("📋 Booth-by-Booth Results", expanded=False):
    st.dataframe(live_df, use_container_width=True, hide_index=True)
