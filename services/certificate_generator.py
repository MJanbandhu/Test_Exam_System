import os
import qrcode
from io import BytesIO
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from config import Config
from utils.logger import logger

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations()
            super().showPage()
        super().save()

    def draw_page_decorations(self):
        self.saveState()
        w, h = landscape(letter)
        
        # Outer Gold Border
        self.setStrokeColor(colors.HexColor('#d4af37'))
        self.setLineWidth(4)
        self.rect(20, 20, w - 40, h - 40)
        
        # Inner Navy Border
        self.setStrokeColor(colors.HexColor('#0f172a'))
        self.setLineWidth(1.5)
        self.rect(26, 26, w - 52, h - 52)
        
        # Corner Accents
        self.setFillColor(colors.HexColor('#d4af37'))
        corner_size = 12
        self.rect(20, h - 20 - corner_size, corner_size, corner_size, fill=1)
        self.rect(w - 20 - corner_size, h - 20 - corner_size, corner_size, corner_size, fill=1)
        self.rect(20, 20, corner_size, corner_size, fill=1)
        self.rect(w - 20 - corner_size, 20, corner_size, corner_size, fill=1)
        
        self.restoreState()

def generate_qr_code_image(cert_id, exam_id):
    qr_content = f"AI Smart Exam Certificate\nID: {cert_id}\nExam: {exam_id}\nVerified: True"
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=4,
        border=2,
    )
    qr.add_data(qr_content)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#0f172a", back_color="white")
    
    img_buffer = BytesIO()
    img.save(img_buffer, format="PNG")
    img_buffer.seek(0)
    return img_buffer

def generate_certificate_pdf(exam, certificate_id):
    """
    Generates a landscape certificate PDF file using ReportLab.
    """
    os.makedirs(Config.CERTIFICATES_DIR, exist_ok=True)
    filename = f"{certificate_id}.pdf"
    filepath = os.path.join(Config.CERTIFICATES_DIR, filename)
    
    doc = SimpleDocTemplate(
        filepath,
        pagesize=landscape(letter),
        leftMargin=40,
        rightMargin=40,
        topMargin=40,
        bottomMargin=40
    )
    
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'CertTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=28,
        leading=34,
        textColor=colors.HexColor('#0f172a'),
        alignment=1, # Center
        spaceAfter=5
    )
    
    subtitle_style = ParagraphStyle(
        'CertSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=16,
        textColor=colors.HexColor('#d4af37'),
        alignment=1,
        spaceAfter=20
    )
    
    presented_style = ParagraphStyle(
        'CertPresented',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=12,
        leading=15,
        textColor=colors.HexColor('#64748b'),
        alignment=1,
        spaceAfter=10
    )
    
    name_style = ParagraphStyle(
        'CertName',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=26,
        leading=30,
        textColor=colors.HexColor('#2563eb'),
        alignment=1,
        spaceAfter=15
    )
    
    body_style = ParagraphStyle(
        'CertBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=18,
        textColor=colors.HexColor('#334155'),
        alignment=1,
        spaceAfter=20
    )
    
    meta_style = ParagraphStyle(
        'CertMeta',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=13,
        textColor=colors.HexColor('#475569')
    )

    story = []
    story.append(Spacer(1, 15))
    story.append(Paragraph("AI SMART EXAMINATION PORTAL", subtitle_style))
    story.append(Paragraph("CERTIFICATE OF ACHIEVEMENT", title_style))
    story.append(Paragraph("THIS CERTIFICATE IS PROUDLY PRESENTED TO", presented_style))
    story.append(Paragraph(f"<u>{exam['student_name'].upper()}</u>", name_style))
    
    date_str = str(exam.get('date', ''))[:10]
    percentage_str = f"{exam.get('percentage', 0.0):.1f}%"
    grade_str = exam.get('grade', 'Pass')
    subject_str = exam.get('subject', 'General Subject')
    difficulty_str = exam.get('difficulty', 'Intermediate')
    
    body_text = f"""for successfully demonstrating mastery and passing the official AI-generated examination in<br/>
    <b>{subject_str}</b> ({difficulty_str} Level) with a score of <b>{percentage_str}</b> (Grade <b>{grade_str}</b>)."""
    story.append(Paragraph(body_text, body_style))
    story.append(Spacer(1, 15))
    
    # Bottom Table with QR code, Certificate Metadata, and Signature
    qr_buffer = generate_qr_code_image(certificate_id, exam['id'])
    qr_img = RLImage(qr_buffer, width=1.1*inch, height=1.1*inch)
    
    meta_text = Paragraph(f"""
    <b>Certificate ID:</b> {certificate_id}<br/>
    <b>Issue Date:</b> {date_str}<br/>
    <b>AI Provider:</b> {exam.get('provider', 'AI Engine')}<br/>
    <b>Verification:</b> Verified Authenticated
    """, meta_style)
    
    sig_text = Paragraph("""
    __________________________________<br/>
    <b>AI Examination Authority</b><br/>
    <i>Automated Smart Certification System</i>
    """, ParagraphStyle('Sig', parent=meta_style, alignment=1))
    
    footer_table_data = [
        [qr_img, meta_text, sig_text]
    ]
    
    footer_table = Table(footer_table_data, colWidths=[1.3*inch, 3.8*inch, 3.2*inch])
    footer_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ALIGN', (0,0), (0,0), 'LEFT'),
        ('ALIGN', (1,1), (1,1), 'LEFT'),
        ('ALIGN', (2,2), (2,2), 'CENTER'),
    ]))
    
    story.append(footer_table)
    
    doc.build(story, canvasmaker=NumberedCanvas)
    logger.info(f"Generated Certificate PDF at: {filepath}")
    return filepath
