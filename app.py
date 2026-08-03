import os
import sys
import uuid
import webbrowser
from threading import Timer
from flask import Flask, render_template, request, jsonify, session, send_file, redirect, url_for

from config import Config
from database.database import init_db
from database.models import StudentModel, ExamModel, QuestionModel, AnswerModel, CertificateModel
from utils.validators import validate_student_name, validate_api_key
from utils.notifications import make_response
from utils.logger import logger
from services.openai_service import verify_openai_api_key
from services.gemini_service import verify_gemini_api_key
from services.exam_generator import generate_exam_questions
from services.evaluator import evaluate_exam_submission

app = Flask(__name__)
app.config.from_object(Config)
Config.init_app(app)

# Initialize database schema on launch
with app.app_context():
    init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/connect-api', methods=['POST'])
def connect_api():
    """
    Validates API key for OpenAI or Gemini and stores in transient session memory.
    """
    data = request.get_json() or {}
    provider = data.get('provider', '').strip()
    api_key = data.get('api_key', '').strip()

    if not provider:
        return make_response(False, "AI Provider must be selected.", notification_type="error", status_code=400)

    # Check for Demo / Mock mode
    if provider.lower() in ['mock', 'demo'] or api_key.upper() in ['MOCK-API-KEY', 'DEMO-KEY', 'DEMO']:
        session['ai_provider'] = 'Mock'
        session['api_key'] = 'MOCK-API-KEY'
        return make_response(True, "Mock AI Connected Successfully (Offline Demo Mode)", 
                             data={"provider": "Mock", "status": "Connected"}, 
                             notification_type="success")

    valid_format, msg = validate_api_key(provider, api_key)
    if not valid_format:
        return make_response(False, msg, notification_type="error", status_code=400)

    if provider.lower() == 'openai':
        is_valid, msg = verify_openai_api_key(api_key)
    elif provider.lower() in ['google gemini', 'gemini']:
        is_valid, msg = verify_gemini_api_key(api_key)
        provider = 'Gemini'
    else:
        return make_response(False, "Unsupported AI Provider.", notification_type="error", status_code=400)

    if is_valid:
        session['ai_provider'] = provider
        session['api_key'] = api_key
        return make_response(True, msg, data={"provider": provider, "status": "Connected"}, notification_type="success")
    else:
        return make_response(False, msg, notification_type="error", status_code=400)

@app.route('/generate-exam', methods=['POST'])
def generate_exam():
    """
    Generates 30 MCQs for the chosen subject and difficulty, saves exam to DB.
    """
    data = request.get_json() or {}
    student_name = data.get('student_name', '').strip()
    subject = data.get('subject', '').strip()
    difficulty = data.get('difficulty', 'Intermediate').strip()
    provider = session.get('ai_provider') or data.get('provider', 'Mock')
    api_key = session.get('api_key') or data.get('api_key', 'MOCK-API-KEY')

    # Validate student name
    valid_name, name_or_err = validate_student_name(student_name)
    if not valid_name:
        return make_response(False, name_or_err, notification_type="error", status_code=400)
    student_name = name_or_err

    if not subject:
        return make_response(False, "Subject name is required.", notification_type="error", status_code=400)

    try:
        # Create student record
        student = StudentModel.create_or_get(student_name)
        student_id = student['id']

        # Generate 30 questions
        questions = generate_exam_questions(
            provider=provider,
            api_key=api_key,
            subject=subject,
            difficulty=difficulty,
            count=30
        )

        exam_id = str(uuid.uuid4())
        ExamModel.create_exam(
            exam_id=exam_id,
            student_id=student_id,
            student_name=student_name,
            subject=subject,
            difficulty=difficulty,
            provider=provider,
            total_questions=len(questions),
            duration=30
        )

        QuestionModel.save_questions(exam_id, questions)

        # Retrieve questions without correct answer for examination view
        client_questions = QuestionModel.get_questions_for_exam(exam_id, include_answers=False)

        return make_response(True, "Examination created successfully!", data={
            "exam_id": exam_id,
            "student_name": student_name,
            "subject": subject,
            "difficulty": difficulty,
            "total_questions": len(client_questions),
            "duration_minutes": 30,
            "questions": client_questions
        }, notification_type="success")
    except Exception as e:
        logger.error(f"Error generating exam: {str(e)}")
        return make_response(False, f"Failed to generate examination: {str(e)}", notification_type="error", status_code=500)

@app.route('/submit-exam', methods=['POST'])
def submit_exam():
    """
    Submits student answers, computes scores & grade, saves results, generates certificate if passed.
    """
    data = request.get_json() or {}
    exam_id = data.get('exam_id')
    student_answers = data.get('answers', {})
    time_taken = int(data.get('time_taken', 0))

    if not exam_id:
        return make_response(False, "Exam ID is required.", notification_type="error", status_code=400)

    try:
        result_payload = evaluate_exam_submission(exam_id, student_answers, time_taken)
        return make_response(True, "Exam submitted and evaluated successfully!", data=result_payload, notification_type="success")
    except Exception as e:
        logger.error(f"Error evaluating exam: {str(e)}")
        return make_response(False, f"Failed to evaluate exam: {str(e)}", notification_type="error", status_code=500)

@app.route('/result/<exam_id>', methods=['GET'])
def get_result(exam_id):
    """
    Retrieves full exam result breakdown including questions with explanations.
    """
    exam = ExamModel.get_by_id(exam_id)
    if not exam:
        return make_response(False, "Exam record not found.", notification_type="error", status_code=404)

    questions = QuestionModel.get_questions_for_exam(exam_id, include_answers=True)
    answers = AnswerModel.get_answers_for_exam(exam_id)
    cert = CertificateModel.get_by_exam(exam_id)

    return make_response(True, "Result fetched successfully", data={
        "exam": exam,
        "questions": questions,
        "answers": answers,
        "certificate": cert
    })

@app.route('/certificate/<exam_id>', methods=['GET'])
def get_certificate(exam_id):
    """
    Retrieves certificate information for passed exam.
    """
    exam = ExamModel.get_by_id(exam_id)
    if not exam:
        return make_response(False, "Exam record not found.", notification_type="error", status_code=404)

    if exam.get('status') != 'Pass':
        return make_response(False, "Certificate is only available for passed examinations.", notification_type="warning", status_code=400)

    cert = CertificateModel.get_by_exam(exam_id)
    return make_response(True, "Certificate fetched successfully", data={
        "exam": exam,
        "certificate": cert
    })

@app.route('/history', methods=['GET'])
def get_history():
    """
    Retrieves exam history with optional search and filter.
    """
    search = request.args.get('search', '')
    subject = request.args.get('subject', '')
    difficulty = request.args.get('difficulty', '')
    status = request.args.get('status', '')

    history = ExamModel.get_all_history(
        search=search,
        subject_filter=subject,
        difficulty_filter=difficulty,
        status_filter=status
    )
    return make_response(True, "Exam history retrieved.", data={"history": history})

@app.route('/history/<exam_id>', methods=['DELETE'])
def delete_history(exam_id):
    """
    Deletes an exam record from history.
    """
    try:
        ExamModel.delete_exam(exam_id)
        return make_response(True, "Exam history deleted successfully.", notification_type="success")
    except Exception as e:
        return make_response(False, f"Failed to delete history: {str(e)}", notification_type="error", status_code=500)

@app.route('/download-result/<exam_id>', methods=['GET'])
def download_result_pdf(exam_id):
    filename = f"result_{exam_id}.pdf"
    filepath = os.path.join(Config.RESULTS_DIR, filename)
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True, download_name=filename)
    else:
        # Re-generate if missing
        exam = ExamModel.get_by_id(exam_id)
        if not exam:
            return "Result file not found", 404
        questions = QuestionModel.get_questions_for_exam(exam_id, include_answers=True)
        answers = AnswerModel.get_answers_for_exam(exam_id)
        from services.pdf_generator import generate_result_pdf
        filepath = generate_result_pdf(exam, questions, answers)
        return send_file(filepath, as_attachment=True, download_name=filename)

@app.route('/download-certificate/<exam_id>', methods=['GET'])
def download_certificate_pdf(exam_id):
    cert = CertificateModel.get_by_exam(exam_id)
    if cert and os.path.exists(cert['pdf_location']):
        filename = f"Certificate_{cert['certificate_id']}.pdf"
        return send_file(cert['pdf_location'], as_attachment=True, download_name=filename)
    else:
        return "Certificate not found or candidate did not pass.", 404

def open_browser():
    webbrowser.open_new('http://127.0.0.1:5000/')

if __name__ == '__main__':
    # Automatically launch default browser after 1.5 seconds
    if not os.environ.get("WERKZEUG_RUN_MAIN"):
        Timer(1.5, open_browser).start()
    app.run(host='127.0.0.1', port=5000, debug=True)
