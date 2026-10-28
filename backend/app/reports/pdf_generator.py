import html
import io
from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import (
    HRFlowable,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


def generate_audit_pdf(audit: Any, pages: list[Any], issues: list[Any]) -> bytes:
    """
    Generates a professional executive PDF SEO audit report using ReportLab.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36,
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=22,
        leading=26,
        textColor=colors.HexColor("#0f172a"),
        spaceAfter=6,
    )
    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=11,
        leading=15,
        textColor=colors.HexColor("#475569"),
        spaceAfter=15,
    )
    h2_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=14,
        leading=18,
        textColor=colors.HexColor("#1e293b"),
        spaceBefore=14,
        spaceAfter=8,
    )
    body_style = ParagraphStyle(
        "DocBody",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#334155"),
    )
    table_cell_style = ParagraphStyle(
        "TableCell",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#1e293b"),
    )
    table_cell_bold = ParagraphStyle(
        "TableCellBold", parent=table_cell_style, fontName="Helvetica-Bold"
    )

    story = []

    # Title & Header
    story.append(Paragraph("SEO Audit Pro — Executive Audit Report", title_style))
    story.append(
        Paragraph(
            f"AI Website SEO Audit & Fix Prioritizer | Domain: <b>{audit.normalized_domain}</b>",
            subtitle_style,
        )
    )
    story.append(
        HRFlowable(
            width="100%", thickness=1.5, color=colors.HexColor("#cbd5e1"), spaceAfter=14
        )
    )

    # Audit Overview KPI Grid
    health_score = audit.seo_health_score or 100.0
    score_color = (
        "#16a34a"
        if health_score >= 80
        else ("#d97706" if health_score >= 60 else "#dc2626")
    )

    overview_data = [
        [
            Paragraph(f"<b>Website Target:</b><br/>{html.escape(str(audit.submitted_url))}", body_style),
            Paragraph(
                f"<b>Audit Date:</b><br/>{audit.created_at.strftime('%Y-%m-%d %H:%M UTC')}",
                body_style,
            ),
            Paragraph(
                f"<b>SEO Health Score:</b><br/><font color='{score_color}' size='14'><b>{health_score:.1f} / 100</b></font>",
                body_style,
            ),
        ],
        [
            Paragraph(f"<b>Pages Crawled:</b><br/>{len(pages)} pages", body_style),
            Paragraph(
                f"<b>Total Issues Detected:</b><br/>{len(issues)} issues", body_style
            ),
            Paragraph(f"<b>Status:</b><br/>{audit.status.upper()}", body_style),
        ],
    ]

    overview_table = Table(overview_data, colWidths=[200, 170, 170])
    overview_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
                ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#e2e8f0")),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    story.append(overview_table)
    story.append(Spacer(1, 15))

    # Severity Breakdown
    story.append(Paragraph("Issue Severity Distribution", h2_style))
    sev_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0, "informational": 0}
    for iss in issues:
        sev = iss.severity.lower()
        if sev in sev_counts:
            sev_counts[sev] += 1

    sev_table_data = [
        [
            Paragraph("<b>Critical</b>", table_cell_bold),
            Paragraph("<b>High</b>", table_cell_bold),
            Paragraph("<b>Medium</b>", table_cell_bold),
            Paragraph("<b>Low</b>", table_cell_bold),
            Paragraph("<b>Advisory</b>", table_cell_bold),
        ],
        [
            Paragraph(
                f"<font color='#dc2626' size='12'><b>{sev_counts['critical']}</b></font>",
                body_style,
            ),
            Paragraph(
                f"<font color='#ea580c' size='12'><b>{sev_counts['high']}</b></font>",
                body_style,
            ),
            Paragraph(
                f"<font color='#d97706' size='12'><b>{sev_counts['medium']}</b></font>",
                body_style,
            ),
            Paragraph(
                f"<font color='#2563eb' size='12'><b>{sev_counts['low']}</b></font>",
                body_style,
            ),
            Paragraph(
                f"<font color='#64748b' size='12'><b>{sev_counts['informational']}</b></font>",
                body_style,
            ),
        ],
    ]
    sev_table = Table(sev_table_data, colWidths=[108, 108, 108, 108, 108])
    sev_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    story.append(sev_table)
    story.append(Spacer(1, 15))

    # Prioritized Fix Roadmap
    story.append(
        Paragraph(
            "Prioritized Fix Roadmap (Ordered by Implementation Priority)", h2_style
        )
    )
    story.append(
        Paragraph(
            "Priority Score is computed using our deterministic formula: <i>100 × (0.45×Impact + 0.30×Scope + 0.25×Confidence) × (1 - 0.15×Effort)</i>.",
            body_style,
        )
    )
    story.append(Spacer(1, 6))

    issues_sorted = sorted(
        issues, key=lambda x: getattr(x, "priority_score", 0.0), reverse=True
    )
    fix_table_data = [
        [
            Paragraph("<b>Rank</b>", table_cell_bold),
            Paragraph("<b>Priority</b>", table_cell_bold),
            Paragraph("<b>Severity</b>", table_cell_bold),
            Paragraph("<b>Issue & Recommended Action</b>", table_cell_bold),
            Paragraph("<b>Scope</b>", table_cell_bold),
            Paragraph("<b>Effort</b>", table_cell_bold),
        ]
    ]

    for idx, iss in enumerate(issues_sorted[:12], start=1):
        sev_color = (
            "#dc2626"
            if iss.severity == "critical"
            else ("#ea580c" if iss.severity == "high" else "#d97706")
        )
        effort_label = (
            "Low"
            if iss.estimated_effort < 0.25
            else ("Medium" if iss.estimated_effort < 0.55 else "High")
        )
        safe_title = html.escape(str(iss.title))
        safe_fix = html.escape(str(iss.suggested_fix))
        action_para = Paragraph(
            f"<b>{safe_title}</b><br/><font color='#475569'>{safe_fix}</font>",
            table_cell_style,
        )
        fix_table_data.append(
            [
                Paragraph(f"#{idx}", table_cell_bold),
                Paragraph(f"<b>{iss.priority_score:.0f}</b>/100", table_cell_bold),
                Paragraph(
                    f"<font color='{sev_color}'><b>{iss.severity.upper()}</b></font>",
                    table_cell_style,
                ),
                action_para,
                Paragraph(f"{iss.affected_page_count} page(s)", table_cell_style),
                Paragraph(effort_label, table_cell_style),
            ]
        )

    fix_table = Table(fix_table_data, colWidths=[36, 48, 60, 290, 56, 50])
    fix_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )
    )
    story.append(fix_table)
    story.append(Spacer(1, 15))

    # Methodology & Disclaimer Note
    story.append(Paragraph("Audit Methodology & Disclaimer", h2_style))
    story.append(
        Paragraph(
            "This audit was executed using safe, rate-limited crawling adhering to robots.txt policy and SSRF security controls. "
            "The SEO Health Score reflects technical adherence to indexability, on-page structure, internal link equity, and schema standards. "
            "A score of 100/100 denotes zero defects identified by these automated checks and is an internal diagnostic benchmark, not an external guarantee of Google search ranking.",
            body_style,
        )
    )

    doc.build(story)
    return buffer.getvalue()
