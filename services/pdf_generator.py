import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from config import Config
from utils.logger import logger

def generate_result_pdf(exam, questions, answers):
    """
    Generates a PDF exam result breakdown document.
    """
    os.makedirs(Config.RESULTS_DIR, exist_ok=True)
    filename = f"result_{exam['id']}.pdf"
    filepath = os.path.join(Config.RESULTS_DIR, filename)
    
    doc = SimpleDocTemplate(
        filepath,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )
    
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'ResultTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        textColor=colors.HexColor('#0f172a'),
        alignment=0,
        spaceAfter=5
    )
    
    sub_style = ParagraphStyle(
        'ResultSub',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        textColor=colors.HexColor('#64748b'),
        spaceAfter=15
    )
    
    h2_style = ParagraphStyle(
        'ResultH2',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=14,
        textColor=colors.HexColor('#1e293b'),
        spaceBefore=10,
        spaceAfter=8
    )
    
    body_style = ParagraphStyle(
        'ResultBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12
    )

    story = []
    story.append(Paragraph("AI Smart Examination Report", title_style))
    story.append(Paragraph(f"Official Performance Evaluation Summary | Exam ID: {exam['id']}", sub_style))
    
    # Meta Information Table
    date_str = str(exam.get('date', ''))[:16]
    time_taken_mins = round(exam.get('time_taken', 0) / 60, 1)
    
    status_color = '#16a34a' if exam.get('status') == 'Pass' else '#dc2626'
    
    meta_data = [
        [
            Paragraph(f"<b>Candidate Name:</b> {exam['student_name']}", body_style),
            Paragraph(f"<b>Date & Time:</b> {date_str}", body_style)
        ],
        [
            Paragraph(f"<b>Subject:</b> {exam['subject']}", body_style),
            Paragraph(f"<b>Time Taken:</b> {time_taken_mins} Mins", body_style)
        ],
        [
            Paragraph(f"<b>Difficulty:</b> {exam['difficulty']}", body_style),
            Paragraph(f"<b>AI Provider:</b> {exam.get('provider', 'AI Engine')}", body_style)
        ],
        [
            Paragraph(f"<b>Score:</b> {exam['score']} / {exam['total_questions']}", body_style),
            Paragraph(f"<b>Percentage:</b> {exam.get('percentage', 0.0):.1f}%", body_style)
        ],
        [
            Paragraph(f"<b>Grade:</b> {exam['grade']}", body_style),
            Paragraph(f"<b>Status:</b> <font color='{status_color}'><b>{exam['status']}</b></font>", body_style)
        ]
    ]
    
    meta_table = Table(meta_data, colWidths=[270, 270])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#e2e8f0')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    
    story.append(meta_table)
    story.append(Spacer(1, 15))
    
    # Questions Breakdown
    story.append(Paragraph("Question Evaluation Breakdown", h2_style))
    
    q_table_data = [
        ["#", "Question", "Your Answer", "Correct Answer", "Result"]
    ]
    
    for idx, q in enumerate(questions, 1):
        q_id = q['id']
        ans = answers.get(str(q_id), {})
        std_ans = ans.get('answer') or 'Skipped'
        corr_ans = q['correct_answer']
        
        if std_ans == 'Skipped':
            res_str = "<font color='#64748b'>Skipped</font>"
        elif std_ans == corr_ans:
            res_str = "<font color='#16a34a'>Correct</font>"
        else:
            res_str = "<font color='#dc2626'>Wrong</font>"
            
        q_text_short = q['question'][:75] + '...' if len(q['question']) > 75 else q['question']
        
        q_table_data.append([
            str(idx),
            Paragraph(q_text_short, body_style),
            std_ans,
            corr_ans,
            Paragraph(res_str, body_style)
        ])
        
    q_table = Table(q_table_data, colWidths=[25, 275, 75, 80, 85])
    q_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0f172a')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 9),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f8fafc')]),
        ('PADDING', (0,0), (-1,-1), 4),
    ]))
    
    story.append(q_table)
    doc.build(story)
    logger.info(f"Generated Result PDF at: {filepath}")
    return filepath
