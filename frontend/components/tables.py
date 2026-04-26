"""Table rendering components using Streamlit."""
import pandas as pd
import streamlit as st


def render_candidate_table(candidates_df: pd.DataFrame):
    """Render formatted candidate table."""
    if candidates_df is None or (hasattr(candidates_df, "empty") and candidates_df.empty):
        st.info("No candidate data available.")
        return

    display_cols = [c for c in ["name", "party", "party_abbrev", "ballot_position"] if c in candidates_df.columns]
    if display_cols:
        st.dataframe(candidates_df[display_cols], use_container_width=True, hide_index=True)
    else:
        st.dataframe(candidates_df, use_container_width=True, hide_index=True)


def render_booth_table(booths_df: pd.DataFrame):
    """Render booth results table with formatting."""
    if booths_df is None or (hasattr(booths_df, "empty") and booths_df.empty):
        st.info("No booth data available.")
        return

    priority_cols = ["booth_id", "booth_name", "counted_pct", "total_primary_counted", "total_enrolled"]
    display_cols = [c for c in priority_cols if c in booths_df.columns]
    remaining = [c for c in booths_df.columns if c not in display_cols]
    display_cols = display_cols + remaining

    st.dataframe(
        booths_df[display_cols],
        use_container_width=True,
        hide_index=True,
        column_config={
            "counted_pct": st.column_config.ProgressColumn(
                "Counted %", format="%.1f%%", min_value=0, max_value=100
            ) if "counted_pct" in booths_df.columns else None,
        }
    )


def render_tcp_summary(tcp_data: dict):
    """Render TCP summary metrics."""
    if not tcp_data:
        st.info("No TCP data available.")
        return

    col1, col2, col3 = st.columns(3)
    candidates = list(tcp_data.keys())

    if len(candidates) >= 1:
        with col1:
            st.metric(
                label=candidates[0],
                value=f"{tcp_data[candidates[0]]:,}",
                help="TCP votes for first candidate"
            )

    if len(candidates) >= 2:
        with col2:
            st.metric(
                label=candidates[1],
                value=f"{tcp_data[candidates[1]]:,}",
                help="TCP votes for second candidate"
            )

    total = sum(tcp_data.values())
    if total > 0 and len(candidates) >= 2:
        pct_a = tcp_data[candidates[0]] / total * 100
        with col3:
            margin = tcp_data[candidates[0]] - tcp_data[candidates[1]]
            st.metric(
                label="Margin",
                value=f"{margin:+,}",
                delta=f"{pct_a:.1f}% TCP"
            )


def render_vote_type_table(vt_df: pd.DataFrame):
    """Render vote type breakdown table."""
    if vt_df is None or (hasattr(vt_df, "empty") and vt_df.empty):
        st.info("No vote type data available.")
        return

    st.dataframe(vt_df, use_container_width=True, hide_index=True)
