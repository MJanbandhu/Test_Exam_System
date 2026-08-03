from database.models import ExamModel, QuestionModel, AnswerModel, CertificateModel
from utils.helpers import calculate_grade, generate_certificate_id
from services.certificate_generator import generate_certificate_pdf
from services.pdf_generator import generate_result_pdf
from utils.logger import logger
import os
from config import Config

def evaluate_exam_submission(exam_id, student_answers, time_taken_seconds):
    """
    Evaluates exam submission, calculates score & grade, updates DB,
    and generates certificate PDF if passed.
    """
    exam = ExamModel.get_by_id(exam_id)
    if not exam:
        raise ValueError("Exam record not found.")
        
    questions = QuestionModel.get_questions_for_exam(exam_id, include_answers=True)
    total_questions = len(questions) if len(questions) > 0 else 30
    
    correct_count = 0
    wrong_count = 0
    skipped_count = 0
    
    formatted_answers = {}
    
    for q in questions:
        q_id = q['id']
        q_id_str = str(q_id)
        
        # Check student answer
        ans_entry = student_answers.get(q_id_str, {})
        if isinstance(ans_entry, str):
            selected = ans_entry.strip().upper() if ans_entry else None
            is_marked = False
        elif isinstance(ans_entry, dict):
            selected = ans_entry.get('answer')
            if selected:
                selected = selected.strip().upper()
            is_marked = ans_entry.get('is_marked', False)
        else:
            selected = None
            is_marked = False
            
        formatted_answers[q_id_str] = {
            "answer": selected,
            "is_marked": is_marked
        }
        
        correct_ans = q['correct_answer'].upper()
        if not selected:
            skipped_count += 1
        elif selected == correct_ans:
            correct_count += 1
        else:
            wrong_count += 1
            
    # Calculate score & percentage
    score = correct_count
    percentage = (correct_count / total_questions) * 100.0 if total_questions > 0 else 0.0
    grade, status = calculate_grade(percentage)
    
    # Save answers to database
    AnswerModel.save_student_answers(exam_id, formatted_answers)
    
    # Update exam status in DB
    ExamModel.update_result(
        exam_id=exam_id,
        time_taken=time_taken_seconds,
        score=score,
        correct_count=correct_count,
        wrong_count=wrong_count,
        skipped_count=skipped_count,
        percentage=percentage,
        grade=grade,
        status=status
    )
    
    # Reload updated exam record
    updated_exam = ExamModel.get_by_id(exam_id)
    
    # Generate Result PDF
    pdf_result_path = generate_result_pdf(updated_exam, questions, formatted_answers)
    
    # If passed, generate certificate
    certificate_data = None
    if status == 'Pass':
        cert_id = generate_certificate_id()
        pdf_cert_path = generate_certificate_pdf(updated_exam, cert_id)
        CertificateModel.create(
            certificate_id=cert_id,
            student_id=updated_exam['student_id'],
            exam_id=exam_id,
            pdf_location=pdf_cert_path
        )
        certificate_data = {
            "certificate_id": cert_id,
            "pdf_location": pdf_cert_path
        }
        
    return {
        "exam": updated_exam,
        "certificate": certificate_data,
        "pdf_result_path": pdf_result_path
    }
