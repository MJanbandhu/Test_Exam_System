# AI-Powered Smart Examination & Certification System

A complete, production-quality AI-Powered Smart Examination & Certification System running entirely on your local machine using Python, Flask, SQLite, vanilla JavaScript, and ReportLab.

## Features

- **Dynamic AI Question Generation**: Generates 30 conceptual, industry-relevant MCQs using OpenAI (`gpt-4o-mini`) or Google Gemini (`gemini-1.5-flash`).
- **Offline / Demo Mode**: Built-in high-quality Mock Question Generator for instant testing without API billing.
- **Timed Examination Engine**: 30-minute live countdown timer with visual warnings at 5 minutes and 1 minute, auto-save every 30 seconds, and auto-submit.
- **Question Navigation Grid**: Real-time grid tracking of Answered, Skipped, Marked for Review, and Unanswered questions with keyboard navigation.
- **Instant Evaluation & Analytics**: Real-time scoring, percentage metrics, grade calculation (A+ to Fail), and interactive Chart.js visualizations.
- **Detailed Answer Review**: Step-by-step breakdown of every question with student choices, correct answers, and AI explanations.
- **Professional PDF Certificates**: Automated landscape PDF certificates generated with ReportLab, featuring custom borders, candidate details, signature blocks, and embedded QR code verification.
- **Persistent Exam History**: SQLite tracking for all attempts, searchable, filterable by subject or pass/fail status, with one-click PDF downloads.

## Technology Stack

- **Backend**: Python 3.11+, Flask, SQLite3, ReportLab, QRCode, Pillow, Requests.
- **Frontend**: HTML5, CSS3 (Glassmorphism & Dark/Light mode tokens), Vanilla JavaScript, Chart.js, Font Awesome.

## How to Run

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Start the application:
   ```bash
   python app.py
   ```
3. The system will automatically open your default browser to `http://127.0.0.1:5000`.

![alt text](<Screenshot 2026-08-04 at 00-05-47 AI Smart Examination & Certification System.png>)
