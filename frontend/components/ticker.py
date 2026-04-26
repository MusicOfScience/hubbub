"""Ticker/simulcast bar for live updates."""
from typing import List

import streamlit as st


def render_ticker(messages: List[str]):
    """Display ticker messages as a styled info bar."""
    if not messages:
        return

    combined = "  •  ".join(messages)
    st.markdown(
        f"""
        <div class="ticker-bar">
            <span class="ticker-label">📡 LIVE</span>
            <span class="ticker-content">{combined}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def get_ticker_messages(election_data: dict) -> List[str]:
    """Auto-generate key facts for the ticker from election state."""
    messages = []

    election = election_data.get("election")
    if election:
        messages.append(f"📍 {election.electorate}, {election.state}")
        messages.append(f"🗓️ Election: {election.election_date}")
        messages.append(f"👥 Enrolled: {election.enrolled_voters:,}")

    live_df = election_data.get("live_count")
    if live_df is not None and not live_df.empty:
        tcp_cols = [c for c in live_df.columns if "_tcp" in c]
        if len(tcp_cols) >= 2:
            total_a = live_df[tcp_cols[0]].sum()
            total_b = live_df[tcp_cols[1]].sum()
            margin = int(total_a - total_b)
            leader = tcp_cols[0].replace("_tcp", "").replace("_", " ").title()
            sign = "+" if margin > 0 else ""
            messages.append(f"🗳️ TCP Margin: {sign}{margin:,} ({leader})")

        primary_cols = [c for c in live_df.columns if "_primary" in c]
        if primary_cols and "total_enrolled" in live_df.columns:
            counted = live_df[primary_cols].sum().sum()
            enrolled = live_df["total_enrolled"].sum()
            pct = counted / enrolled * 100 if enrolled > 0 else 0
            messages.append(f"📊 Count Progress: {pct:.1f}%")

    if not messages:
        messages.append("🗳️ Margin of Error — Australian election analysis")

    return messages
