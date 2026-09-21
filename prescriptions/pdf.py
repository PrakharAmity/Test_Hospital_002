import io
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def generate_prescription_pdf(prescription):
    """
    Generate an offline, high-quality PDF prescription using ReportLab.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()
    story = []

    title_style = ParagraphStyle(
        'HospitalTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        textColor=colors.HexColor('#1e293b'),
        spaceAfter=4,
    )
    subtitle_style = ParagraphStyle(
        'HospitalSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        textColor=colors.HexColor('#64748b'),
        spaceAfter=15,
    )
    section_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading3'],
        fontName='Helvetica-Bold',
        fontSize=12,
        textColor=colors.HexColor('#0f766e'),
        spaceBefore=10,
        spaceAfter=6,
    )
    normal_style = ParagraphStyle(
        'RegularText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        textColor=colors.HexColor('#334155'),
    )

    # Hospital Header
    story.append(Paragraph("MEDLEDGER HEALTHCARE SYSTEM", title_style))
    story.append(Paragraph("Multi-Specialty Hospital & Medical Research Center • Offline Medical Records", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0f766e'), spaceAfter=15))

    patient = prescription.appointment.patient
    doctor = prescription.appointment.doctor

    # Patient & Doctor Info Table
    info_data = [
        [
            Paragraph(f"<b>Patient Name:</b> {patient.full_name}", normal_style),
            Paragraph(f"<b>Attending Doctor:</b> Dr. {doctor.name}", normal_style),
        ],
        [
            Paragraph(f"<b>Blood Group:</b> {patient.blood_group}", normal_style),
            Paragraph(f"<b>Department:</b> {doctor.department}", normal_style),
        ],
        [
            Paragraph(f"<b>Date of Birth:</b> {patient.date_of_birth}", normal_style),
            Paragraph(f"<b>Appointment Date:</b> {prescription.appointment.date}", normal_style),
        ],
        [
            Paragraph(f"<b>Phone:</b> {patient.phone}", normal_style),
            Paragraph(f"<b>Prescription ID:</b> {str(prescription.id)[:8]}", normal_style),
        ],
    ]

    info_table = Table(info_data, colWidths=[260, 260])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 15))

    # Rx Medicines Table
    story.append(Paragraph("Rx / Prescribed Medications", section_style))

    med_rows = [["#", "Medicine Name", "Dosage", "Instructions"]]
    medicines = prescription.medicines if isinstance(prescription.medicines, list) else []

    if not medicines:
        med_rows.append(["1", "General Regimen", prescription.dosage, prescription.instructions])
    else:
        for idx, med in enumerate(medicines, 1):
            name = med.get('name', 'Prescribed Medicine') if isinstance(med, dict) else str(med)
            dosage = med.get('dosage', prescription.dosage) if isinstance(med, dict) else prescription.dosage
            timing = med.get('instructions', prescription.instructions) if isinstance(med, dict) else prescription.instructions
            med_rows.append([str(idx), name, dosage, timing])

    med_table = Table(med_rows, colWidths=[30, 180, 140, 170])
    med_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0f766e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(med_table)
    story.append(Spacer(1, 15))

    # General Advice
    story.append(Paragraph("Physician Advice & Instructions", section_style))
    story.append(Paragraph(prescription.instructions or "Take medications as prescribed.", normal_style))
    story.append(Spacer(1, 25))

    # Doctor Signature Line
    story.append(HRFlowable(width="40%", thickness=1, color=colors.HexColor('#94a3b8'), spaceAfter=5, hAlign='RIGHT'))
    sig_style = ParagraphStyle(
        'DoctorSig',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        textColor=colors.HexColor('#1e293b'),
        alignment=2 # Right aligned
    )
    story.append(Paragraph(f"Dr. {doctor.name} ({doctor.department})", sig_style))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
