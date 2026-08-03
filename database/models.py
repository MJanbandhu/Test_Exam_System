import uuid
from datetime import datetime
from database.database import get_db

class StudentModel:
    @staticmethod
    def create_or_get(name):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM students WHERE LOWER(name) = LOWER(?)", (name.strip(),))
        existing = cursor.fetchone()
        if existing:
            conn.close()
            return existing
        cursor.execute("INSERT INTO students (name) VALUES (?)", (name.strip(),))
        student_id = cursor.lastrowid
        conn.commit()
        cursor.execute("SELECT * FROM students WHERE id = ?", (student_id,))
        student = cursor.fetchone()
        conn.close()
        return student

class ExamModel:
    @staticmethod
    def create_exam(exam_id, student_id, student_name, subject, difficulty, provider, total_questions=30, duration=30):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO exams (id, student_id, student_name, subject, difficulty, provider, total_questions, duration, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'Pending')
        """, (exam_id, student_id, student_name, subject, difficulty, provider, total_questions, duration))
        conn.commit()
        conn.close()
        return exam_id

    @staticmethod
    def get_by_id(exam_id):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM exams WHERE id = ?", (exam_id,))
        exam = cursor.fetchone()
        conn.close()
        return exam

    @staticmethod
    def update_result(exam_id, time_taken, score, correct_count, wrong_count, skipped_count, percentage, grade, status):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE exams 
            SET time_taken = ?, score = ?, correct_count = ?, wrong_count = ?, skipped_count = ?, percentage = ?, grade = ?, status = ?
            WHERE id = ?
        """, (time_taken, score, correct_count, wrong_count, skipped_count, percentage, grade, status, exam_id))
        conn.commit()
        conn.close()

    @staticmethod
    def get_all_history(search="", subject_filter="", difficulty_filter="", status_filter=""):
        conn = get_db()
        cursor = conn.cursor()
        query = "SELECT * FROM exams WHERE 1=1"
        params = []

        if search:
            query += " AND (LOWER(student_name) LIKE ? OR LOWER(subject) LIKE ?)"
            term = f"%{search.lower()}%"
            params.extend([term, term])
        if subject_filter:
            query += " AND LOWER(subject) = LOWER(?)"
            params.append(subject_filter)
        if difficulty_filter:
            query += " AND LOWER(difficulty) = LOWER(?)"
            params.append(difficulty_filter)
        if status_filter:
            query += " AND LOWER(status) = LOWER(?)"
            params.append(status_filter)

        query += " ORDER BY date DESC"
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        return rows

    @staticmethod
    def delete_exam(exam_id):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM exams WHERE id = ?", (exam_id,))
        conn.commit()
        conn.close()

class QuestionModel:
    @staticmethod
    def save_questions(exam_id, questions_list):
        conn = get_db()
        cursor = conn.cursor()
        for idx, q in enumerate(questions_list, 1):
            cursor.execute("""
                INSERT INTO questions (exam_id, question_order, question, option_a, option_b, option_c, option_d, correct_answer, explanation)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                exam_id,
                idx,
                q['question'],
                q['option_a'],
                q['option_b'],
                q['option_c'],
                q['option_d'],
                q['correct_answer'].upper(),
                q.get('explanation', '')
            ))
        conn.commit()
        conn.close()

    @staticmethod
    def get_questions_for_exam(exam_id, include_answers=False):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM questions WHERE exam_id = ? ORDER BY question_order ASC", (exam_id,))
        questions = cursor.fetchall()
        conn.close()
        
        if not include_answers:
            for q in questions:
                q.pop('correct_answer', None)
                q.pop('explanation', None)
        return questions

class AnswerModel:
    @staticmethod
    def save_student_answers(exam_id, answers_dict):
        # answers_dict: {question_id: {'answer': 'A', 'is_marked': False}}
        conn = get_db()
        cursor = conn.cursor()
        # Clear previous answers if any
        cursor.execute("DELETE FROM answers WHERE exam_id = ?", (exam_id,))
        
        # Get correct answers
        cursor.execute("SELECT id, correct_answer FROM questions WHERE exam_id = ?", (exam_id,))
        correct_map = {q['id']: q['correct_answer'] for q in cursor.fetchall()}
        
        for q_id_str, ans_data in answers_dict.items():
            q_id = int(q_id_str)
            student_ans = ans_data.get('answer')
            if student_ans:
                student_ans = student_ans.upper()
            is_marked = 1 if ans_data.get('is_marked') else 0
            
            correct_ans = correct_map.get(q_id)
            is_correct = 1 if (student_ans and student_ans == correct_ans) else 0
            
            cursor.execute("""
                INSERT INTO answers (exam_id, question_id, student_answer, is_correct, is_marked)
                VALUES (?, ?, ?, ?, ?)
            """, (exam_id, q_id, student_ans, is_correct, is_marked))
            
        conn.commit()
        conn.close()

    @staticmethod
    def get_answers_for_exam(exam_id):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM answers WHERE exam_id = ?", (exam_id,))
        answers = cursor.fetchall()
        conn.close()
        return {a['question_id']: a for a in answers}

class CertificateModel:
    @staticmethod
    def create(certificate_id, student_id, exam_id, pdf_location):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO certificates (certificate_id, student_id, exam_id, pdf_location)
            VALUES (?, ?, ?, ?)
        """, (certificate_id, student_id, exam_id, pdf_location))
        conn.commit()
        conn.close()

    @staticmethod
    def get_by_exam(exam_id):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM certificates WHERE exam_id = ?", (exam_id,))
        cert = cursor.fetchone()
        conn.close()
        return cert
