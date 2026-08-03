import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'ai-exam-cert-system-super-secret-key-2026')
    DATABASE_PATH = os.path.join(BASE_DIR, 'database.db')
    CERTIFICATES_DIR = os.path.join(BASE_DIR, 'static', 'certificates')
    RESULTS_DIR = os.path.join(BASE_DIR, 'static', 'results')
    
    # Examination Defaults
    DEFAULT_QUESTION_COUNT = 30
    DEFAULT_EXAM_DURATION_MINUTES = 30
    PASSING_PERCENTAGE = 50.0
    
    # AI Providers Config
    OPENAI_DEFAULT_MODEL = "gpt-4o-mini"
    GEMINI_DEFAULT_MODEL = "gemini-1.5-flash"
    
    # Ensure directories exist
    @staticmethod
    def init_app(app=None):
        os.makedirs(Config.CERTIFICATES_DIR, exist_ok=True)
        os.makedirs(Config.RESULTS_DIR, exist_ok=True)
