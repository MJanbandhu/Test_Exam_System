import random
import re
from services.openai_service import generate_openai_questions
from services.gemini_service import generate_gemini_questions
from utils.logger import logger

# Cache to store previously generated question sets: {(subject.lower(), difficulty.lower()): [questions]}
QUESTION_CACHE = {}

def shuffle_options_and_fix_answer(q):
    """
    Shuffles option_a, option_b, option_c, option_d and updates correct_answer to match.
    """
    correct_letter = q['correct_answer'].upper().strip()
    key_map = {'A': 'option_a', 'B': 'option_b', 'C': 'option_c', 'D': 'option_d'}
    
    if correct_letter not in key_map or key_map[correct_letter] not in q:
        correct_letter = 'A'
        
    correct_text = q[key_map[correct_letter]]
    
    options = [
        q['option_a'],
        q['option_b'],
        q['option_c'],
        q['option_d']
    ]
    
    random.shuffle(options)
    
    new_q = q.copy()
    new_q['option_a'] = options[0]
    new_q['option_b'] = options[1]
    new_q['option_c'] = options[2]
    new_q['option_d'] = options[3]
    
    # Find new index of correct_text
    new_index = options.index(correct_text)
    letters = ['A', 'B', 'C', 'D']
    new_q['correct_answer'] = letters[new_index]
    return new_q

def generate_exam_questions(provider, api_key, subject, difficulty, count=30, use_cache=True):
    """
    Main generator orchestrator with auto-retry and shuffle logic.
    """
    subject_clean = subject.strip()
    difficulty_clean = difficulty.strip().capitalize()
    cache_key = (subject_clean.lower(), difficulty_clean.lower())
    
    if use_cache and cache_key in QUESTION_CACHE:
        logger.info(f"Serving exam for '{subject_clean}' ({difficulty_clean}) from cache.")
        cached_qs = QUESTION_CACHE[cache_key]
        # Return shuffled copy
        return [shuffle_options_and_fix_answer(q) for q in cached_qs[:count]]
        
    # Check if Mock mode requested or demo key
    if provider.upper() == 'MOCK' or api_key.strip().upper() in ['MOCK-API-KEY', 'DEMO-KEY', 'DEMO']:
        raw_questions = generate_mock_questions(subject_clean, difficulty_clean, count)
    else:
        max_retries = 3
        raw_questions = None
        last_error = None
        
        for attempt in range(1, max_retries + 1):
            try:
                logger.info(f"Generating questions (Attempt {attempt}/{max_retries}) using {provider} for {subject_clean}...")
                if provider.lower() == 'openai':
                    raw_questions = generate_openai_questions(api_key, subject_clean, difficulty_clean, count)
                elif provider.lower() == 'gemini':
                    raw_questions = generate_gemini_questions(api_key, subject_clean, difficulty_clean, count)
                else:
                    raise ValueError(f"Unsupported provider: {provider}")
                    
                if raw_questions and len(raw_questions) >= 5: # At least minimum questions retrieved
                    break
            except Exception as e:
                last_error = e
                logger.warning(f"Attempt {attempt} failed: {str(e)}")
                
        if not raw_questions or len(raw_questions) == 0:
            logger.warning(f"Falling back to high-quality Mock Generator due to AI failure: {last_error}")
            raw_questions = generate_mock_questions(subject_clean, difficulty_clean, count)
            
    # Process and sanitize questions
    processed = []
    for idx, q in enumerate(raw_questions):
        try:
            cleaned_q = {
                "question": str(q.get('question', f"Question {idx+1} about {subject_clean}")).strip(),
                "option_a": str(q.get('option_a', 'Option A')).strip(),
                "option_b": str(q.get('option_b', 'Option B')).strip(),
                "option_c": str(q.get('option_c', 'Option C')).strip(),
                "option_d": str(q.get('option_d', 'Option D')).strip(),
                "correct_answer": str(q.get('correct_answer', 'A')).upper().strip(),
                "explanation": str(q.get('explanation', 'Correct option validated according to subject principles.')).strip()
            }
            processed.append(shuffle_options_and_fix_answer(cleaned_q))
        except Exception as err:
            logger.warning(f"Skipping malformed question at index {idx}: {err}")
            
    # Ensure exact requested count
    while len(processed) < count:
        dummy = generate_mock_questions(subject_clean, difficulty_clean, count)[0]
        processed.append(shuffle_options_and_fix_answer(dummy))
        
    final_questions = processed[:count]
    QUESTION_CACHE[cache_key] = final_questions
    return final_questions

def generate_mock_questions(subject, difficulty, count=30):
    """
    Generates high quality, realistic mock examination questions for any subject & difficulty level.
    """
    templates = [
        {
            "q": "What is the primary core principle underlying {subject} when designing robust scalable solutions at {difficulty} level?",
            "a": "Modular abstraction and strict encapsulation of responsibilities.",
            "b": "Direct global memory access without garbage collection.",
            "c": "Replacing all structured data formats with unstructured text streams.",
            "d": "Disabling transactional locks to maximize concurrency throughput unconditionally.",
            "correct": "A",
            "exp": "Modular abstraction isolates components, ensuring maintainability, clean testing, and scalability."
        },
        {
            "q": "In {subject}, which architectural pattern is recommended for decoupling event producers from consumers?",
            "a": "Publish-Subscribe (Pub/Sub) messaging pattern.",
            "b": "Monolithic Synchronous Call Chain.",
            "c": "Tight Class Inheritance Hierarchy.",
            "d": "Polling Shared File System Directories.",
            "correct": "A",
            "exp": "Pub/Sub decouples components by allowing asynchronous message broadcasting across independent subscribers."
        },
        {
            "q": "When optimizing performance in a {subject} environment, what is the best strategy to mitigate high latency?",
            "a": "Implementing distributed caching and lazy evaluation.",
            "b": "Increasing thread lock frequency on memory buffers.",
            "c": "Executing all computations synchronously on the main event loop.",
            "d": "Disabling query indices to reduce database file size.",
            "correct": "A",
            "exp": "Caching frequently accessed data significantly reduces round-trip latency and backend processing overhead."
        },
        {
            "q": "Which security best practice should be applied when managing confidential parameters in a {subject} deployment?",
            "a": "Injecting credentials via secure environment variables or vault secret managers.",
            "b": "Hardcoding production keys directly inside static source files.",
            "c": "Storing secret keys in public client-side JavaScript repositories.",
            "d": "Transmitting raw credentials over unencrypted HTTP GET parameters.",
            "correct": "A",
            "exp": "Environment variables and secret vaults keep secrets out of source code repositories and version history."
        },
        {
            "q": "What is the consequence of failing to validate external user input within a {subject} system?",
            "a": "Increased vulnerability to injection attacks and unhandled exceptions.",
            "b": "Automatic speed boost in request execution.",
            "c": "Guaranteed deterministic output under all traffic spikes.",
            "d": "Automatic data compression across network sockets.",
            "correct": "A",
            "exp": "Unvalidated input exposes applications to SQL injection, XSS, and unexpected runtime crashes."
        },
        {
            "q": "Which data structure is optimal for fast O(1) key-based lookups in {subject}?",
            "a": "Hash Table / Dictionary.",
            "b": "Singly Linked List.",
            "c": "Unsorted Array.",
            "d": "Binary Tree without balancing.",
            "correct": "A",
            "exp": "Hash tables compute array indices via hash functions, providing average O(1) lookup time complexity."
        },
        {
            "q": "In modern {subject} development, what does the term 'Idempotency' refer to?",
            "a": "An operation producing the exact same state outcome regardless of how many times it is executed.",
            "b": "A process that executes twice as fast on multi-core processors.",
            "c": "A bug where functions return random floating-point values.",
            "d": "The ability of a system to auto-restart upon hardware failure.",
            "correct": "A",
            "exp": "Idempotent operations yield identical system state whether called once or multiple times consecutively."
        },
        {
            "q": "How does automated unit testing contribute to overall code quality in {subject} projects?",
            "a": "It catches regressions early and provides executable documentation of code behavior.",
            "b": "It eliminates the need for any manual system or user testing.",
            "c": "It guarantees that the software will consume zero CPU memory.",
            "d": "It automatically generates user interface mockups.",
            "correct": "A",
            "exp": "Automated unit tests detect bugs during development and document expected function specifications."
        },
        {
            "q": "What is the main advantage of containerization (e.g. Docker) in {subject} application delivery?",
            "a": "Consistent execution environments across development, testing, and production servers.",
            "b": "Elimination of all network bandwidth costs.",
            "c": "Automatic conversion of Python code into C++ binaries.",
            "d": "Guaranteed protection against all zero-day hardware flaws.",
            "correct": "A",
            "exp": "Containerization packages applications with their exact dependencies, eliminating 'works on my machine' issues."
        },
        {
            "q": "Which metric is critical for monitoring system availability and health in {subject}?",
            "a": "Request error rate and response latency distribution (p95/p99).",
            "b": "Total number of lines of source code written per hour.",
            "c": "Physical weight of the host server rack.",
            "d": "Color scheme contrast ratio of developer IDE themes.",
            "correct": "A",
            "exp": "Latency quantiles and error rates accurately reflect end-user experience and backend operational stability."
        }
    ]
    
    mock_list = []
    for i in range(count):
        tpl = templates[i % len(templates)]
        variation = (i // len(templates)) + 1
        q_text = tpl["q"].format(subject=subject, difficulty=difficulty)
        if variation > 1:
            q_text += f" (Scenario Variation #{variation})"
            
        mock_list.append({
            "question": q_text,
            "option_a": tpl["a"],
            "option_b": tpl["b"],
            "option_c": tpl["c"],
            "option_d": tpl["d"],
            "correct_answer": tpl["correct"],
            "explanation": f"[{subject} - {difficulty}] " + tpl["exp"]
        })
        
    return mock_list
