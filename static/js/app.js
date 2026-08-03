/* Main Application Controller & State Store */

const AppState = {
  studentName: localStorage.getItem('student_name') || '',
  aiProvider: localStorage.getItem('ai_provider') || 'OpenAI',
  apiKeyConnected: false,
  currentView: 'welcome-view',
  theme: localStorage.getItem('theme') || 'dark',
  
  // Active Exam State
  activeExam: null, // { exam_id, questions, duration_minutes, ... }
  studentAnswers: {}, // { question_id: { answer: 'A', is_marked: false } }
  currentQuestionIndex: 0,
  timeRemainingSeconds: 1800,
  timerInterval: null,
  autoSaveInterval: null
};

// API Helper
async function apiCall(endpoint, method = 'GET', payload = null) {
  try {
    const options = {
      method,
      headers: { 'Content-Type': 'application/json' }
    };
    if (payload) options.body = JSON.stringify(payload);

    const response = await fetch(endpoint, options);
    const data = await response.json();
    return data;
  } catch (err) {
    console.error(`API Error on ${endpoint}:`, err);
    return {
      success: false,
      message: "Network or server connection error. Please try again.",
      notification: { type: 'error', message: "Connection Error" }
    };
  }
}

// Navigation & View Router
function showView(viewId) {
  document.querySelectorAll('.view-section').forEach(view => {
    view.classList.remove('active');
  });
  const targetView = document.getElementById(viewId);
  if (targetView) {
    targetView.classList.add('active');
    AppState.currentView = viewId;
    window.scrollTo(0, 0);
  }
}

// Loading Overlay Controls
function showLoading(message = "Processing...") {
  const overlay = document.getElementById('loading-overlay');
  const text = document.getElementById('loading-text');
  if (text) text.textContent = message;
  if (overlay) overlay.style.display = 'flex';
}

function hideLoading() {
  const overlay = document.getElementById('loading-overlay');
  if (overlay) overlay.style.display = 'none';
}

// Theme Toggle
function toggleTheme(theme = null) {
  const newTheme = theme || (AppState.theme === 'dark' ? 'light' : 'dark');
  AppState.theme = newTheme;
  document.documentElement.setAttribute('data-theme', newTheme);
  localStorage.setItem('theme', newTheme);
  NotificationManager.show(`Switched to ${newTheme.toUpperCase()} theme mode.`, 'info');
}

// Initialize on DOM Loaded
document.addEventListener('DOMContentLoaded', () => {
  // Apply saved theme
  document.documentElement.setAttribute('data-theme', AppState.theme);

  // Pre-fill saved student name if any
  const nameInput = document.getElementById('student-name-input');
  if (nameInput && AppState.studentName) {
    nameInput.value = AppState.studentName;
  }

  // Set initial view
  showView('welcome-view');
});
