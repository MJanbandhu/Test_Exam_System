import requests
import json
import re
from utils.logger import logger

def verify_gemini_api_key(api_key):
    """
    Verifies Google Gemini API Key by sending a test payload to models endpoint.
    """
    if not api_key:
        return False, "API key is missing"
    
    key = api_key.strip()
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={key}"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return True, "Google Gemini API Connected Successfully"
        elif response.status_code in [400, 401, 403]:
            return False, "Invalid Google Gemini API Key"
        else:
            return False, f"Gemini verification failed (Status code: {response.status_code})"
    except requests.exceptions.Timeout:
        return False, "Connection Timeout while connecting to Google Gemini"
    except Exception as e:
        logger.error(f"Gemini Verification Exception: {str(e)}")
        return False, f"Network/Connection error: {str(e)}"

def generate_gemini_questions(api_key, subject, difficulty, count=30):
    """
    Generates structured MCQs using Google Gemini API.
    """
    key = api_key.strip()
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={key}"
    
    prompt = f"""You are an expert examination master for {subject}.
Generate exactly {count} unique, conceptual, industry-relevant, practical multiple-choice questions for {subject} at {difficulty} level.

Format your output STRICTLY as a JSON array of objects with NO markdown formatting, NO code blocks, and NO preamble text.
Each JSON object MUST have:
[
  {{
    "question": "Clear question text",
    "option_a": "First option",
    "option_b": "Second option",
    "option_c": "Third option",
    "option_d": "Fourth option",
    "correct_answer": "A",
    "explanation": "Short, clear explanation."
  }}
]
Rules:
1. Difficulty ({difficulty}): Adjust conceptual difficulty accordingly.
2. Ensure correct_answer is exactly one letter: A, B, C, or D.
3. Return ONLY the raw JSON array.
"""

    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }],
        "generationConfig": {
            "temperature": 0.7,
            "responseMimeType": "application/json"
        }
    }
    
    try:
        response = requests.post(url, json=payload, timeout=45)
        if response.status_code != 200:
            # Fallback attempt with gemini-2.0-flash or gemini-pro if 1.5 is unavailable
            url_alt = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={key}"
            response = requests.post(url_alt, json=payload, timeout=45)
            
        if response.status_code != 200:
            logger.error(f"Gemini error status: {response.status_code}, body: {response.text}")
            raise ValueError(f"Google Gemini API Error: {response.status_code}")
            
        data = response.json()
        raw_text = data['candidates'][0]['content']['parts'][0]['text'].strip()
        
        # Clean markdown codeblocks if present
        cleaned_text = re.sub(r'^```json\s*|^```\s*|```$', '', raw_text, flags=re.MULTILINE).strip()
        
        questions = json.loads(cleaned_text)
        if isinstance(questions, dict) and 'questions' in questions:
            questions = questions['questions']
            
        if not isinstance(questions, list) or len(questions) == 0:
            raise ValueError("Returned JSON is not a valid list of questions.")
            
        return questions
    except Exception as e:
        logger.error(f"Failed to generate Gemini questions: {str(e)}")
        raise e
