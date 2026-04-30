from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import json
import os
from ..database import get_db
from ..models import User, ESGData, Report
from ..auth import get_current_user

router = APIRouter(prefix="/reports", tags=["Reports"])

@router.post("/generate/{year}")
async def generate_report(year: int, report_type: str = "basic", db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Get ESG data
    esg_data = db.query(ESGData).filter(
        ESGData.user_id == current_user.id,
        ESGData.reporting_year == year
    ).first()
    
    if not esg_data:
        raise HTTPException(status_code=404, detail="No ESG data found for this year")
    
    # Generate PDF
    pdf_filename = f"reports/{current_user.id}_{year}_{report_type}.pdf"
    os.makedirs("reports", exist_ok=True)
    
    doc = SimpleDocTemplate(pdf_filename, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=24, textColor=colors.HexColor('#2ecc71'))
    story.append(Paragraph(f"ESG Report - {current_user.company_name}", title_style))
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph(f"Reporting Year: {year} | Report Type: {report_type.upper()}", styles['Normal']))
    story.append(Spacer(1, 0.3*inch))
    
    # Environment Section
    story.append(Paragraph("🌍 ENVIRONMENT PERFORMANCE", styles['Heading2']))
    env_data = [
        ["KPI", "Value", "Unit"],
        ["Scope 1 Emissions", f"{esg_data.scope1_emissions}", "tCO2e"],
        ["Scope 2 Emissions", f"{esg_data.scope2_emissions}", "tCO2e"],
        ["Renewable Energy", f"{esg_data.renewable_energy_percentage}", "%"],
        ["Water Consumption", f"{esg_data.total_water_consumption}", "m³"],
        ["Waste Recycled", f"{esg_data.waste_recycled_percentage}", "%"],
    ]
    table = Table(env_data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2ecc71')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    story.append(table)
    story.append(Spacer(1, 0.3*inch))
    
    # Social Section
    story.append(Paragraph("👥 SOCIAL PERFORMANCE", styles['Heading2']))
    social_data = [
        ["KPI", "Value", "Unit"],
        ["Total Employees", f"{esg_data.total_employees}", "FTE"],
        ["Women in Board", f"{esg_data.women_in_board_percentage}", "%"],
        ["Qatarization", f"{esg_data.qatarization_percentage}", "%"],
        ["Safety Training", f"{esg_data.safety_training_completion}", "%"],
        ["LTIFR", f"{esg_data.ltifr}", "per million hours"],
    ]
    table2 = Table(social_data)
    table2.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    story.append(table2)
    story.append(Spacer(1, 0.3*inch))
    
    # Governance Section
    story.append(Paragraph("⚖️ GOVERNANCE PERFORMANCE", styles['Heading2']))
    gov_data = [
        ["KPI", "Value", "Unit"],
        ["Anti-bribery Policy", "Yes" if esg_data.has_antibribery_policy else "No", ""],
        ["Suppliers ESG Screened", f"{esg_data.supplier_esg_screened}", "%"],
        ["Local Procurement", f"{esg_data.local_procurement_percentage}", "%"],
        ["Data Breaches", f"{esg_data.data_breaches_count}", "incidents"],
    ]
    table3 = Table(gov_data)
    table3.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e74c3c')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    story.append(table3)
    
    # Build PDF
    doc.build(story)
    
    # Save to database
    with open(pdf_filename, 'rb') as f:
        report_data = f.read()
    
    new_report = Report(
        user_id=current_user.id,
        report_type=report_type,
        report_data={
            "year": year,
            "esg_data": {
                "environment": {"scope1": esg_data.scope1_emissions, "scope2": esg_data.scope2_emissions},
                "social": {"employees": esg_data.total_employees, "women_board": esg_data.women_in_board_percentage},
                "governance": {"antibribery": esg_data.has_antibribery_policy}
            }
        },
        pdf_path=pdf_filename
    )
    db.add(new_report)
    db.commit()
    
    return {"message": "Report generated", "filename": pdf_filename, "download_url": f"/reports/download/{new_report.id}"}

@router.get("/download/{report_id}")
def download_report(report_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    report = db.query(Report).filter(Report.id == report_id, Report.user_id == current_user.id).first()
    if not report or not report.pdf_path:
        raise HTTPException(status_code=404, detail="Report not found")
    
    return FileResponse(report.pdf_path, media_type="application/pdf", filename=f"esg_report_{report_id}.pdf")

@router.get("/history")
def get_report_history(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    reports = db.query(Report).filter(Report.user_id == current_user.id).order_by(Report.created_at.desc()).all()
    return [
        {
            "id": r.id,
            "report_type": r.report_type,
            "created_at": r.created_at,
            "download_url": f"/reports/download/{r.id}"
        }
        for r in reports
    ]