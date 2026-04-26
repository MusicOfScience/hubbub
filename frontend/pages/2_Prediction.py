"""Prediction page — Monte Carlo probability of victory."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import numpy as np
import pandas as pd
import streamlit as st

from backend.analysis.live_count import calculate_tcp_margin
from backend.analysis.monte_carlo import MonteCarloEngine
from backend.analysis.poll_aggregator import PollAggregator
from frontend.components.charts import probability_bell_curve

st.set_page_config(page_title="Prediction — MOE", page_icon="🔮", layout="wide")

css_path = Path(__file__).parent.parent / "styles" / "custom.css"
if css_path.exists():
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.title("🔮 Prediction")

live_df: pd.DataFrame = st.session_state.get("live_count", pd.DataFrame())
election = st.session_state.get("election")

# ── Derive base margin from live count ────────────────────────────────────────
if live_df is not None and not live_df.empty:
    base_margin, _ = calculate_tcp_margin(live_df)
else:
    base_margin = 800  # sample default if no live data

# ── MC Settings ───────────────────────────────────────────────────────────────
st.markdown("### Monte Carlo Settings")
col_s1, col_s2, col_s3 = st.columns(3)
with col_s1:
    n_iterations = st.slider("Iterations", 1000, 50000, 10000, step=1000)
with col_s2:
    std_dev = st.slider("Std Dev (votes)", 200, 5000, 1500, step=100)
with col_s3:
    manual_margin = st.number_input("Override Base Margin", value=base_margin, step=100)

if st.button("🚀 Run Simulation", type="primary"):
    engine = MonteCarloEngine(base_margin=manual_margin, std_dev=std_dev)
    results = engine.run_simulation(n_iterations=n_iterations)
    st.session_state["mc_results"] = results
    st.session_state["mc_engine"] = engine
    st.session_state["mc_margin"] = manual_margin
    st.session_state["mc_std"] = std_dev

# ── Results Display ────────────────────────────────────────────────────────────
mc_results = st.session_state.get("mc_results")
mc_engine: MonteCarloEngine = st.session_state.get("mc_engine")
mc_margin = st.session_state.get("mc_margin", manual_margin)
mc_std = st.session_state.get("mc_std", std_dev)

if mc_results is not None and mc_engine is not None:
    st.markdown("---")
    alp_prob = mc_engine.probability_of_victory(mc_results, "ALP")
    lib_prob = 1 - alp_prob
    ci_low, ci_high = mc_engine.confidence_interval(mc_results, 0.95)

    col1, col2, col3, col4 = st.columns(4)
    alp_c = "#E53935"
    lib_c = "#1565C0"
    col1.markdown(
        f'<div style="text-align:center"><div style="font-size:2.5rem;font-weight:800;color:{alp_c}">{alp_prob*100:.1f}%</div><div>ALP (Chen)</div></div>',
        unsafe_allow_html=True,
    )
    col2.markdown(
        f'<div style="text-align:center"><div style="font-size:2.5rem;font-weight:800;color:{lib_c}">{lib_prob*100:.1f}%</div><div>LIB (Morrison)</div></div>',
        unsafe_allow_html=True,
    )
    col3.metric("95% CI Low", f"{ci_low:+,}")
    col4.metric("95% CI High", f"{ci_high:+,}")

    # Bell curve
    st.markdown("---")
    fig = probability_bell_curve(mc_margin, mc_std)
    st.plotly_chart(fig, use_container_width=True)

    # Scenario details
    with st.expander("📋 Simulation Details"):
        st.write(f"Iterations: {len(mc_results):,}")
        st.write(f"Mean: {mc_results.mean():.0f}")
        st.write(f"Std Dev: {mc_results.std():.0f}")
        st.write(f"Min: {mc_results.min():.0f} | Max: {mc_results.max():.0f}")
else:
    st.info("⬆️ Configure settings and click **Run Simulation** to see probability of victory.")
    # Preview chart with defaults
    fig = probability_bell_curve(base_margin, 1500)
    st.plotly_chart(fig, use_container_width=True)

# ── Poll Aggregator ────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### Poll Aggregator")

if "polls" not in st.session_state:
    st.session_state["polls"] = []

with st.expander("➕ Add Poll", expanded=False):
    with st.form("add_poll_form"):
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            poll_date = st.date_input("Poll Date")
            pollster = st.text_input("Pollster", "YouGov")
        with col_p2:
            alp_pct = st.number_input("ALP %", 0.0, 100.0, 38.0, 0.5)
            lib_pct = st.number_input("LIB %", 0.0, 100.0, 35.0, 0.5)
            grn_pct = st.number_input("GRN %", 0.0, 100.0, 14.0, 0.5)
            ind_pct = st.number_input("IND %", 0.0, 100.0, 10.0, 0.5)
            others_pct = max(0.0, 100.0 - alp_pct - lib_pct - grn_pct - ind_pct)
        submitted = st.form_submit_button("Add Poll")
        if submitted:
            st.session_state["polls"].append({
                "date": str(poll_date),
                "pollster": pollster,
                "alp": alp_pct,
                "lib": lib_pct,
                "grn": grn_pct,
                "ind": ind_pct,
                "others": others_pct,
            })
            st.success("Poll added!")

polls = st.session_state.get("polls", [])
if polls:
    agg = PollAggregator()
    for p in polls:
        agg.add_poll(p)
    aggregated = agg.get_aggregated_primary_votes()

    st.markdown("**Aggregated Primary Votes (exponential decay, 14-day half-life)**")
    agg_df = pd.DataFrame([aggregated])
    st.dataframe(agg_df, use_container_width=True, hide_index=True)

    polls_df = pd.DataFrame(polls)
    st.markdown("**Poll History**")
    st.dataframe(polls_df, use_container_width=True, hide_index=True)
else:
    st.info("No polls added yet. Use the form above to add poll data.")
