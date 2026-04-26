"""Preference model page — adjust flows and calculate TCP."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pandas as pd
import streamlit as st

from backend.analysis.preferences import PreferenceModel

st.set_page_config(page_title="Preference Model — MOE", page_icon="🔢", layout="wide")

css_path = Path(__file__).parent.parent / "styles" / "custom.css"
if css_path.exists():
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.title("🔢 Preference Model")

election = st.session_state.get("election")
candidates = st.session_state.get("candidates", [])

# ── Build preference model ────────────────────────────────────────────────────
pref_model = PreferenceModel(election.candidates if election else [])
flows = pref_model.default_pref_flows()

# ── Display preference flow matrix ────────────────────────────────────────────
st.markdown("### Current Preference Flow Matrix")
matrix_data = []
for party, dests in flows.items():
    row = {"From Party": party}
    row.update({f"→ {k}": f"{v*100:.0f}%" for k, v in dests.items()})
    matrix_data.append(row)

matrix_df = pd.DataFrame(matrix_data)
st.dataframe(matrix_df, use_container_width=True, hide_index=True)

# ── Adjust flows ──────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### Adjust Preference Flows")

non_tcp_parties = ["GRN", "IND", "ONP", "OTH"]
adjusted_flows = {}

cols = st.columns(len(non_tcp_parties))
for i, party in enumerate(non_tcp_parties):
    with cols[i]:
        st.markdown(f"**{party}**")
        default_alp = int(flows.get(party, {}).get("ALP", 0.5) * 100)
        alp_flow = st.slider(
            f"{party} → ALP (%)", 0, 100, default_alp, 1, key=f"pref_{party}"
        )
        lib_flow = 100 - alp_flow
        st.caption(f"→ LIB: {lib_flow}%")
        adjusted_flows[party] = {"ALP": alp_flow / 100, "LIB": lib_flow / 100}

# Three-way contest toggle
st.markdown("---")
three_way = st.toggle("Enable Three-Way Contest Mode", value=False)

# Primary votes for calculation
st.markdown("### Primary Vote Inputs")
col_pv1, col_pv2 = st.columns(2)
with col_pv1:
    alp_primary = st.number_input("ALP Primary %", 0.0, 100.0, 38.0, 0.5)
    lib_primary = st.number_input("LIB Primary %", 0.0, 100.0, 35.0, 0.5)
with col_pv2:
    grn_primary = st.number_input("GRN Primary %", 0.0, 100.0, 14.0, 0.5)
    ind_primary = st.number_input("IND Primary %", 0.0, 100.0, 10.0, 0.5)
    informal_pct = max(0.0, 100.0 - alp_primary - lib_primary - grn_primary - ind_primary)
    st.metric("Informal/Others", f"{informal_pct:.1f}%")

primary_votes = {
    "ALP": alp_primary, "LIB": lib_primary,
    "GRN": grn_primary, "IND": ind_primary, "informal": informal_pct,
}

if st.button("📊 Calculate Expected TCP", type="primary"):
    if three_way:
        # Three-way: find who gets eliminated first
        three_votes = {"ALP": alp_primary, "LIB": lib_primary, "GRN": grn_primary + ind_primary}
        eliminated, remaining = pref_model.three_way_contest_resolution(three_votes)
        st.info(f"**Three-way resolution:** {eliminated} eliminated. Final contest: {remaining[0]} vs {remaining[1]}")

    tcp = pref_model.flow_to_tcp(primary_votes, adjusted_flows)
    alp_tcp = tcp.get("ALP", 50.0)
    lib_tcp = tcp.get("LIB", 50.0)
    margin_pp = alp_tcp - lib_tcp

    st.markdown("---")
    st.markdown("### TCP Result")
    col_t1, col_t2, col_t3 = st.columns(3)
    winner_colour = "#E53935" if alp_tcp > 50 else "#1565C0"
    winner = "ALP (Chen)" if alp_tcp > 50 else "LIB (Morrison)"

    col_t1.markdown(
        f'<div style="font-size:2rem;font-weight:700;color:#E53935">{alp_tcp:.2f}%</div><div>ALP TCP</div>',
        unsafe_allow_html=True,
    )
    col_t2.markdown(
        f'<div style="font-size:2rem;font-weight:700;color:#1565C0">{lib_tcp:.2f}%</div><div>LIB TCP</div>',
        unsafe_allow_html=True,
    )
    col_t3.markdown(
        f'<div style="font-size:2rem;font-weight:700;color:{winner_colour}">{margin_pp:+.2f}pp</div><div>{winner} leads</div>',
        unsafe_allow_html=True,
    )

    exhaustion = pref_model.calculate_exhaustion_rate()
    st.caption(f"Exhaustion rate: {exhaustion*100:.1f}% (federal compulsory preferential)")

# Show flow matrix with adjustments
st.markdown("---")
with st.expander("📋 Adjusted Flow Matrix"):
    adj_matrix = []
    for party, dests in adjusted_flows.items():
        adj_matrix.append({"Party": party, "→ ALP": f"{dests['ALP']*100:.0f}%", "→ LIB": f"{dests['LIB']*100:.0f}%"})
    st.dataframe(pd.DataFrame(adj_matrix), use_container_width=True, hide_index=True)
