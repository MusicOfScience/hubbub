"""Export page — download reports in various formats."""
import sys
from pathlib import Path
import io

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pandas as pd
import streamlit as st

from backend.export.exporter import Exporter

st.set_page_config(page_title="Export — MOE", page_icon="⬇️", layout="wide")

css_path = Path(__file__).parent.parent / "styles" / "custom.css"
if css_path.exists():
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.title("⬇️ Export")

election = st.session_state.get("election")
live_df: pd.DataFrame = st.session_state.get("live_count", pd.DataFrame())

if not election:
    st.info("No election data loaded. Return to the home page.")
    st.stop()

exporter = Exporter(election=election, live_data=live_df if live_df is not None else pd.DataFrame())

# ── Briefing report ───────────────────────────────────────────────────────────
st.markdown("### Briefing Report")
briefing = exporter.briefing_report()
st.markdown(briefing)

st.markdown("---")

# ── Download buttons ──────────────────────────────────────────────────────────
st.markdown("### Downloads")
col_d1, col_d2, col_d3 = st.columns(3)

# CSV
with col_d1:
    st.markdown("**CSV Export**")
    if live_df is not None and not live_df.empty:
        csv_buffer = live_df.to_csv(index=False)
        st.download_button(
            label="⬇️ Download Live Count CSV",
            data=csv_buffer,
            file_name=f"{election.election_id}_live_count.csv",
            mime="text/csv",
        )
    else:
        st.info("No live count data to export.")

# XLSX
with col_d2:
    st.markdown("**Excel Export**")
    try:
        xlsx_bytes = exporter.to_xlsx_bytes()
        st.download_button(
            label="⬇️ Download XLSX",
            data=xlsx_bytes,
            file_name=f"{election.election_id}_report.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    except Exception as e:
        st.error(f"XLSX export error: {e}")

# HTML report
with col_d3:
    st.markdown("**HTML Report**")
    html_content = exporter.to_html_string()
    st.download_button(
        label="⬇️ Download HTML Report",
        data=html_content.encode("utf-8"),
        file_name=f"{election.election_id}_report.html",
        mime="text/html",
    )

# ── Commentary export ──────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### Commentary Export")
commentary = st.session_state.get("commentary", [])
intelligence = st.session_state.get("intelligence", [])

col_e1, col_e2 = st.columns(2)
with col_e1:
    if commentary:
        comm_df = pd.DataFrame(commentary)
        st.download_button(
            label="⬇️ Commentary CSV",
            data=comm_df.to_csv(index=False),
            file_name="commentary.csv",
            mime="text/csv",
        )
    else:
        st.info("No commentary to export.")

with col_e2:
    if intelligence:
        intel_df = pd.DataFrame(intelligence)
        st.download_button(
            label="⬇️ Intelligence CSV",
            data=intel_df.to_csv(index=False),
            file_name="intelligence.csv",
            mime="text/csv",
        )
    else:
        st.info("No intelligence to export.")

# ── Full data preview ──────────────────────────────────────────────────────────
st.markdown("---")
with st.expander("📋 Live Count Data Preview"):
    if live_df is not None and not live_df.empty:
        st.dataframe(live_df, use_container_width=True, hide_index=True)
    else:
        st.info("No live count data available.")
