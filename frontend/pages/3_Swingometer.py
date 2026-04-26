"""Swingometer — interactive swing scenario builder."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pandas as pd
import streamlit as st

from backend.analysis.swing import apply_swing_scenario
from backend.analysis.preferences import PreferenceModel
from backend.analysis.monte_carlo import MonteCarloEngine

st.set_page_config(page_title="Swingometer — MOE", page_icon="📐", layout="wide")

css_path = Path(__file__).parent.parent / "styles" / "custom.css"
if css_path.exists():
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.title("📐 Swingometer")

election = st.session_state.get("election")
scenario = st.session_state.get("scenario", {})

# Base votes from scenario or defaults
BASE_VOTES = {"ALP": 38.0, "LIB": 35.0, "GRN": 14.0, "IND": 10.0, "informal": 3.0}

# ── Controls ──────────────────────────────────────────────────────────────────
st.markdown("### Primary Vote Swings")
col1, col2 = st.columns(2)

with col1:
    st.markdown("**Party Swings (percentage points)**")
    swing_alp = st.slider("ALP Swing", -10.0, 10.0, float(scenario.get("swing_alp", 0.0)), 0.1)
    swing_lib = st.slider("LIB Swing", -10.0, 10.0, float(scenario.get("swing_lib", 0.0)), 0.1)
    swing_grn = st.slider("GRN Swing", -10.0, 10.0, float(scenario.get("swing_grn", 0.0)), 0.1)
    swing_ind = st.slider("IND Swing", -10.0, 10.0, float(scenario.get("swing_ind", 0.0)), 0.1)

with col2:
    st.markdown("**Preference Flows**")
    grn_to_alp = st.slider(
        "GRN → ALP (%)", 0, 100,
        int(scenario.get("grn_to_alp_pref", 75)), 1,
    )
    grn_to_lib = 100 - grn_to_alp
    st.caption(f"GRN → LIB: {grn_to_lib}%")

    ind_to_alp = st.slider(
        "IND → ALP (%)", 0, 100,
        int(scenario.get("ind_to_alp_pref", 55)), 1,
    )
    ind_to_lib = 100 - ind_to_alp
    st.caption(f"IND → LIB: {ind_to_lib}%")

    st.markdown("**Other Settings**")
    postal_alp = st.slider("Postal ALP %", 30, 70, int(scenario.get("postal_alp_lean", 46)), 1)
    turnout = st.slider("Turnout %", 80.0, 100.0, float(scenario.get("turnout_pct", 94.0)), 0.5)
    informal = st.slider("Informal %", 0.0, 10.0, float(scenario.get("informal_pct", 3.0)), 0.1)

# ── Calculate ─────────────────────────────────────────────────────────────────
swings = {"ALP": swing_alp, "LIB": swing_lib, "GRN": swing_grn, "IND": swing_ind}
adjusted_votes = apply_swing_scenario(BASE_VOTES, swings)
adjusted_votes["informal"] = informal

pref_model = PreferenceModel(election.candidates if election else [])
pref_model.adjust_preference_flow("GRN", "ALP", float(grn_to_alp))
pref_model.adjust_preference_flow("IND", "ALP", float(ind_to_alp))
pref_matrix = pref_model._pref_flows

tcp_result = pref_model.flow_to_tcp(adjusted_votes, pref_matrix)
alp_tcp = tcp_result.get("ALP", 50.0)
lib_tcp = tcp_result.get("LIB", 50.0)

# Enrolled voters for margin calc
enrolled = election.enrolled_voters if election else 35420
formal_votes = int(enrolled * (turnout / 100) * (1 - informal / 100))
alp_tcp_votes = int(formal_votes * alp_tcp / 100)
lib_tcp_votes = int(formal_votes * lib_tcp / 100)
margin = alp_tcp_votes - lib_tcp_votes

# ── Results ───────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### Scenario Result")

col_r1, col_r2, col_r3 = st.columns(3)
winner_colour = "#E53935" if margin > 0 else "#1565C0"
winner = "ALP (Chen)" if margin > 0 else "LIB (Morrison)"

with col_r1:
    st.markdown(
        f'<div class="margin-display" style="color:{winner_colour}">{margin:+,}</div>',
        unsafe_allow_html=True,
    )
    st.caption(f"Winner: **{winner}**")
with col_r2:
    st.metric("ALP TCP", f"{alp_tcp:.1f}%", delta=f"{alp_tcp - 50:.1f}pp from 50%")
with col_r3:
    st.metric("LIB TCP", f"{lib_tcp:.1f}%", delta=f"{lib_tcp - 50:.1f}pp from 50%")

# MC probability
mc = MonteCarloEngine(base_margin=margin, std_dev=1200)
mc_results = mc.run_simulation(5000)
alp_prob = mc.probability_of_victory(mc_results, "ALP")

st.markdown(
    f"**Probability of ALP victory under this scenario:** "
    f'<span style="font-size:1.4rem;font-weight:700;color:#E53935">{alp_prob*100:.1f}%</span>',
    unsafe_allow_html=True,
)

# ── Vote share breakdown ──────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### Adjusted Primary Votes")
votes_display = {k: round(v, 2) for k, v in adjusted_votes.items()}
votes_df = pd.DataFrame([votes_display]).T.reset_index()
votes_df.columns = ["Party", "Vote Share (%)"]
st.dataframe(votes_df, use_container_width=True, hide_index=True)

# ── Save / Load / Reset ───────────────────────────────────────────────────────
st.markdown("---")
col_save, col_reset = st.columns(2)
with col_save:
    if st.button("💾 Save Scenario to Session"):
        st.session_state["scenario"].update({
            "swing_alp": swing_alp, "swing_lib": swing_lib,
            "swing_grn": swing_grn, "swing_ind": swing_ind,
            "grn_to_alp_pref": float(grn_to_alp), "grn_to_lib_pref": float(grn_to_lib),
            "ind_to_alp_pref": float(ind_to_alp), "ind_to_lib_pref": float(ind_to_lib),
            "postal_alp_lean": float(postal_alp), "turnout_pct": turnout, "informal_pct": informal,
        })
        st.success("Scenario saved to session state.")
with col_reset:
    if st.button("🔄 Reset to Defaults"):
        st.session_state["scenario"] = {
            "swing_alp": 0.0, "swing_lib": 0.0, "swing_grn": 0.0, "swing_ind": 0.0,
            "grn_to_alp_pref": 75.0, "grn_to_lib_pref": 25.0,
            "ind_to_alp_pref": 55.0, "ind_to_lib_pref": 45.0,
            "postal_alp_lean": 46.0, "turnout_pct": 94.0, "informal_pct": 3.0,
        }
        st.rerun()
