import requests
import json
from utils.logger import logger

def verify_openai_api_key(api_key):
    """
    Verifies OpenAI API key by making a lightweight request to models endpoint.
    """
    if not api_key:
        return False, "API key is missing"
    
    url = "https://api.openai.com/v1/models"
    headers = {
        "Authorization": f"Bearer {api_key.strip()}"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return True, "OpenAI API Connected Successfully"
        elif response.status_code == 401:
            return False, "Invalid OpenAI API Key"
        else:
            return False, f"OpenAI verification failed (Status code: {response.status_code})"
    except requests.exceptions.Timeout:
        return False, "Connection Timeout while connecting to OpenAI"
    except Exception as e:
        logger.error(f"OpenAI Verification Exception: {str(e)}")
        return False, f"Network/Connection error: {str(e)}"

def generate_openai_questions(api_key, subject, difficulty, count=30):
    """
    Generates structured MCQs using OpenAI GPT model.
    """
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key.strip()}",
        "Content-Type": "application/json"
    }
    
    prompt = f"""You are an expert examiner for {subject}.
Generate exactly {count} unique, conceptual, industry-relevant, practical multiple-choice questions for {subject} at {difficulty} level.

Format your output STRICTLY as a JSON array of objects with no markdown formatting or commentary. Each object MUST have the following structure:
[
  {{
    "question": "Clear, practical problem statement or conceptual question",
    "option_a": "First option text",
    "option_b": "Second option text",
    "option_c": "Third option text",
    "option_d": "Fourth option text",
    "correct_answer": "A", // Must be one of 'A', 'B', 'C', 'D'
    "explanation": "Short, clear explanation of why this answer is correct."
  }}
]
Rules:
1. Difficulty level ({difficulty}): Adjust technical depth, scenario complexity, and vocabulary accordingly.
2. No duplicate questions.
3. Keep options clear and unambiguous.
4. Return ONLY valid JSON array.
"""

    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": "You are a professional examination generator. Output valid JSON arrays only."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "response_format": {"type": "json_object"} if False else None
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=45)
        if response.status_code != 200:
            logger.error(f"OpenAI error status: {response.status_code}, body: {response.text}")
            raise ValueError(f"OpenAI API Error: {response.status_code}")
            
        data = response.json()
        content = data['choices'][0]['message']['content'].strip()
        
        # Strip markdown json backticks if present
        if content.startswith("```"):
            content = re.sub(r'^```json\s*|^```\s*|```$', '', content, flags=re.MULTILINE).strip()
            
        questions = json.loads(content)
        if isinstance(questions, dict) and 'questions' in questions:
            questions = questions['questions']
            
        if not isinstance(questions, list) or len(questions) == 0:
            raise ValueError("Returned JSON is not a valid list of questions.")
            
        return questions
    except Exception as e:
        logger.error(f"Failed to generate OpenAI questions: {str(e)}")
        raise e
