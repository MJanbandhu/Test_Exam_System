import re

def validate_student_name(name):
    """
    Validates student name:
    - Not empty
    - Only alphabets and spaces allowed
    - Minimum length 3 characters
    """
    if not name or not isinstance(name, str):
        return False, "Student name is required."
    
    clean_name = name.strip()
    if len(clean_name) < 3:
        return False, "Student name must be at least 3 characters long."
    
    if not re.match(r'^[a-zA-Z\s]+$', clean_name):
        return False, "Student name can only contain alphabets and spaces."
        
    return True, clean_name

def validate_api_key(provider, api_key):
    """
    Basic structural check for API Key format before remote verification
    """
    if not api_key or not isinstance(api_key, str) or not api_key.strip():
        return False, f"API key for {provider} cannot be empty."
    
    key = api_key.strip()
    if provider.lower() == 'openai':
        if not (key.startswith('sk-') or len(key) > 20):
            return False, "Invalid OpenAI API Key format. Key usually starts with 'sk-'."
    elif provider.lower() == 'gemini':
        if len(key) < 15:
            return False, "Invalid Google Gemini API Key format."
            
    return True, key
