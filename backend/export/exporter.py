"""Export election data to various formats."""
import io
from datetime import datetime

import pandas as pd

from backend.models.election import Election


class Exporter:
    """Export election data to CSV, XLSX, HTML, and markdown."""

    def __init__(self, election: Election, live_data: pd.DataFrame):
        self.election = election
        self.live_data = live_data

    def to_csv(self, path: str) -> str:
        """Export live data to CSV. Returns path."""
        self.live_data.to_csv(path, index=False)
        return path

    def to_xlsx(self, path: str) -> str:
        """Export live data to XLSX with formatted sheets. Returns path."""
        with pd.ExcelWriter(path, engine="xlsxwriter") as writer:
            workbook = writer.book

            # Summary sheet
            summary_data = {
                "Field": [
                    "Election ID", "Electorate", "State", "Level",
                    "Election Date", "Enrolled Voters", "TCP Candidate 1", "TCP Candidate 2"
                ],
                "Value": [
                    self.election.election_id, self.election.electorate,
                    self.election.state, self.election.level,
                    self.election.election_date, self.election.enrolled_voters,
                    self.election.tcp_candidates[0] if self.election.tcp_candidates else "",
                    self.election.tcp_candidates[1] if len(self.election.tcp_candidates) > 1 else "",
                ]
            }
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name="Summary", index=False)

            # Format summary sheet
            worksheet = writer.sheets["Summary"]
            header_fmt = workbook.add_format({"bold": True, "bg_color": "#1565C0", "font_color": "white"})
            worksheet.set_column("A:A", 20)
            worksheet.set_column("B:B", 30)
            worksheet.write(0, 0, "Field", header_fmt)
            worksheet.write(0, 1, "Value", header_fmt)

            # Live count sheet
            if not self.live_data.empty:
                self.live_data.to_excel(writer, sheet_name="Live Count", index=False)
                ws2 = writer.sheets["Live Count"]
                for i, col in enumerate(self.live_data.columns):
                    ws2.write(0, i, col, header_fmt)
                ws2.set_column(0, len(self.live_data.columns), 15)

        return path

    def to_xlsx_bytes(self) -> bytes:
        """Return XLSX as bytes for in-memory download."""
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
            workbook = writer.book
            header_fmt = workbook.add_format({"bold": True, "bg_color": "#1565C0", "font_color": "white"})

            summary_data = {
                "Field": ["Election ID", "Electorate", "State", "Level", "Election Date", "Enrolled Voters"],
                "Value": [
                    self.election.election_id, self.election.electorate,
                    self.election.state, self.election.level,
                    self.election.election_date, self.election.enrolled_voters,
                ]
            }
            pd.DataFrame(summary_data).to_excel(writer, sheet_name="Summary", index=False)
            ws = writer.sheets["Summary"]
            ws.set_column("A:A", 20)
            ws.set_column("B:B", 30)
            ws.write(0, 0, "Field", header_fmt)
            ws.write(0, 1, "Value", header_fmt)

            if not self.live_data.empty:
                self.live_data.to_excel(writer, sheet_name="Live Count", index=False)
                ws2 = writer.sheets["Live Count"]
                for i, col in enumerate(self.live_data.columns):
                    ws2.write(0, i, col, header_fmt)
                ws2.set_column(0, len(self.live_data.columns), 15)

        return buffer.getvalue()

    def to_html_report(self, path: str) -> str:
        """Generate a basic HTML report. Returns path."""
        html = self._build_html()
        with open(path, "w") as f:
            f.write(html)
        return path

    def to_html_string(self) -> str:
        """Return HTML report as string."""
        return self._build_html()

    def _build_html(self) -> str:
        election = self.election
        rows = ""
        if not self.live_data.empty:
            rows = self.live_data.to_html(index=False, border=0, classes="data-table")

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Margin of Error - {election.electorate} {election.election_date}</title>
<style>
body {{ font-family: Arial, sans-serif; margin: 20px; color: #333; }}
h1 {{ color: #1565C0; }}
h2 {{ color: #E53935; }}
.data-table {{ border-collapse: collapse; width: 100%; }}
.data-table th {{ background: #1565C0; color: white; padding: 8px; }}
.data-table td {{ padding: 6px; border-bottom: 1px solid #ddd; }}
.meta {{ background: #f5f5f5; padding: 12px; border-radius: 4px; }}
</style>
</head>
<body>
<h1>🗳️ Margin of Error</h1>
<h2>{election.electorate} — {election.election_date}</h2>
<div class="meta">
  <p><strong>State:</strong> {election.state} &nbsp;|&nbsp;
     <strong>Level:</strong> {election.level} &nbsp;|&nbsp;
     <strong>Enrolled:</strong> {election.enrolled_voters:,}</p>
  <p><strong>TCP:</strong> {" vs ".join(election.tcp_candidates)}</p>
  <p><em>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</em></p>
</div>
<h2>Live Count Data</h2>
{rows if rows else "<p>No live count data available.</p>"}
</body>
</html>"""

    def briefing_report(self) -> str:
        """Return a markdown formatted briefing."""
        election = self.election
        lines = [
            f"# Margin of Error — Briefing Report",
            f"## {election.electorate}, {election.state} ({election.level})",
            f"**Election Date:** {election.election_date}",
            f"**Enrolled Voters:** {election.enrolled_voters:,}",
            f"**TCP Contest:** {' vs '.join(election.tcp_candidates)}",
            f"",
            f"## Candidates",
        ]
        for c in election.candidates:
            lines.append(f"- **{c['name']}** ({c['party_abbrev']}) — {c['party']}")
        lines.append("")
        lines.append("## Vote Type Estimates")
        for vtype, count in election.vote_type_estimates.items():
            lines.append(f"- {vtype.replace('_', ' ').title()}: {count:,}")
        lines.append("")
        lines.append(f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*")
        return "\n".join(lines)
