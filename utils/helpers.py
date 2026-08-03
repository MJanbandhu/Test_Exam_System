import uuid
import datetime

def calculate_grade(percentage):
    """
    Grade System:
    90-100: A+
    80-89:  A
    70-79:  B
    60-69:  C
    50-59:  D
    Below 50: Fail
    """
    pct = round(percentage, 2)
    if pct >= 90.0:
        return 'A+', 'Pass'
    elif pct >= 80.0:
        return 'A', 'Pass'
    elif pct >= 70.0:
        return 'B', 'Pass'
    elif pct >= 60.0:
        return 'C', 'Pass'
    elif pct >= 50.0:
        return 'D', 'Pass'
    else:
        return 'Fail', 'Fail'

def generate_certificate_id():
    year = datetime.datetime.now().year
    short_hash = uuid.uuid4().hex[:8].upper()
    return f"CERT-{year}-{short_hash}"

def format_seconds(seconds):
    mins = seconds // 60
    secs = seconds % 60
    return f"{mins:02d}:{secs:02d}"
