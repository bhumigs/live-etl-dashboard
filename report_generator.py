# report_generator.py
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
import pandas as pd
import datetime
import os


def generate_pdf_report(df: pd.DataFrame):
    """Generate a PDF summary report of the filtered data."""

    # Ensure reports folder exists
    reports_dir = "reports"
    os.makedirs(reports_dir, exist_ok=True)

    # File name with timestamp
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    pdf_path = os.path.join(reports_dir, f"etl_report_{timestamp}.pdf")

    # PDF document setup
    doc = SimpleDocTemplate(pdf_path, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    # Title
    elements.append(Paragraph("📊 ETL Dashboard Report", styles['Title']))
    elements.append(Spacer(1, 12))

    # Summary
    elements.append(Paragraph(
        f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph(f"Total Rows: {len(df)}", styles['Normal']))
    elements.append(Spacer(1, 12))

    # Add basic stats
    summary = df.describe(include='all').fillna("").round(2)
    summary_table = Table([summary.columns.tolist()] + summary.values.tolist())

    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))

    elements.append(summary_table)
    elements.append(Spacer(1, 12))

    # Build PDF
    doc.build(elements)
    return pdf_path
