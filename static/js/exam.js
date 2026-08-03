/* Active Examination Interface & Countdown Timer Engine */

function initExamInterface() {
  if (!AppState.activeExam) return;

  const exam = AppState.activeExam;

  // Header info
  document.getElementById('exam-header-name').textContent = AppState.studentName;
  document.getElementById('exam-header-subject').textContent = exam.subject;
  document.getElementById('exam-header-difficulty').textContent = exam.difficulty;

  // Render Question Grid Nav
  renderQuestionGridNav();

  // Load first question
  loadQuestion(0);

  // Start Timer
  startExamTimer();

  // Start Auto-Save interval (every 30s)
  if (AppState.autoSaveInterval) clearInterval(AppState.autoSaveInterval);
  AppState.autoSaveInterval = setInterval(autoSaveProgress, 30000);

  // Bind Keyboard Shortcuts
  document.removeEventListener('keydown', handleExamKeydown);
  document.addEventListener('keydown', handleExamKeydown);
}

// Timer Controller
function startExamTimer() {
  if (AppState.timerInterval) clearInterval(AppState.timerInterval);

  const timerDisplay = document.getElementById('exam-timer-display');
  const timerBox = document.getElementById('timer-box-container');

  function updateDisplay() {
    const mins = Math.floor(AppState.timeRemainingSeconds / 60);
    const secs = AppState.timeRemainingSeconds % 60;
    const timeStr = `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;

    if (timerDisplay) timerDisplay.textContent = timeStr;

    // Warnings
    if (AppState.timeRemainingSeconds === 300) { // 5 mins
      NotificationManager.show("Warning: 5 minutes remaining!", "warning");
      if (timerBox) timerBox.className = 'timer-box warning';
    } else if (AppState.timeRemainingSeconds === 60) { // 1 min
      NotificationManager.show("Warning: 1 minute remaining! Exam will auto-submit.", "error");
      if (timerBox) timerBox.className = 'timer-box danger';
    } else if (AppState.timeRemainingSeconds <= 0) {
      clearInterval(AppState.timerInterval);
      NotificationManager.show("Time expired! Automatically submitting examination.", "error");
      autoSubmitExam();
    }
  }

  updateDisplay();
  AppState.timerInterval = setInterval(() => {
    AppState.timeRemainingSeconds--;
    updateDisplay();
  }, 1000);
}

// Question Navigation Grid
function renderQuestionGridNav() {
  const container = document.getElementById('question-grid-container');
  if (!container || !AppState.activeExam) return;

  container.innerHTML = '';
  const total = AppState.activeExam.questions.length;

  for (let i = 0; i < total; i++) {
    const btn = document.createElement('button');
    btn.className = 'q-nav-btn';
    btn.textContent = i + 1;
    btn.onclick = () => loadQuestion(i);
    btn.id = `q-nav-btn-${i}`;
    container.appendChild(btn);
  }
  updateNavGridState();
}

function updateNavGridState() {
  if (!AppState.activeExam) return;
  const questions = AppState.activeExam.questions;

  questions.forEach((q, idx) => {
    const btn = document.getElementById(`q-nav-btn-${idx}`);
    if (!btn) return;

    btn.className = 'q-nav-btn';
    if (idx === AppState.currentQuestionIndex) {
      btn.classList.add('current');
    }

    const qAns = AppState.studentAnswers[q.id];
    if (qAns) {
      if (qAns.is_marked) {
        btn.classList.add('marked');
      } else if (qAns.answer) {
        btn.classList.add('answered');
      } else {
        btn.classList.add('skipped');
      }
    }
  });

  // Update Summary Counts
  let answered = 0, marked = 0, skipped = 0;
  Object.values(AppState.studentAnswers).forEach(a => {
    if (a.is_marked) marked++;
    else if (a.answer) answered++;
    else skipped++;
  });

  const total = questions.length;
  const notAttempted = total - (answered + marked + skipped);

  document.getElementById('nav-count-answered').textContent = answered;
  document.getElementById('nav-count-marked').textContent = marked;
  document.getElementById('nav-count-not-answered').textContent = notAttempted + skipped;
}

// Load Specific Question
function loadQuestion(index) {
  if (!AppState.activeExam || index < 0 || index >= AppState.activeExam.questions.length) return;

  AppState.currentQuestionIndex = index;
  const q = AppState.activeExam.questions[index];

  document.getElementById('current-question-num').textContent = index + 1;
  document.getElementById('total-questions-num').textContent = AppState.activeExam.questions.length;
  document.getElementById('question-text-box').textContent = q.question;

  // Options
  const optionsList = document.getElementById('options-list-container');
  optionsList.innerHTML = '';

  const options = [
    { letter: 'A', text: q.option_a },
    { letter: 'B', text: q.option_b },
    { letter: 'C', text: q.option_c },
    { letter: 'D', text: q.option_d }
  ];

  const currentAns = AppState.studentAnswers[q.id]?.answer;

  options.forEach(opt => {
    const div = document.createElement('div');
    div.className = `option-item ${currentAns === opt.letter ? 'selected' : ''}`;
    div.onclick = () => selectOption(q.id, opt.letter);
    div.innerHTML = `
      <div class="option-letter">${opt.letter}</div>
      <div class="option-text">${opt.text}</div>
    `;
    optionsList.appendChild(div);
  });

  updateNavGridState();
}

function selectOption(qId, letter) {
  if (!AppState.studentAnswers[qId]) {
    AppState.studentAnswers[qId] = { answer: letter, is_marked: false };
  } else {
    AppState.studentAnswers[qId].answer = letter;
  }
  loadQuestion(AppState.currentQuestionIndex);
}

function prevQuestion() {
  if (AppState.currentQuestionIndex > 0) {
    loadQuestion(AppState.currentQuestionIndex - 1);
  }
}

function nextQuestion() {
  if (AppState.activeExam && AppState.currentQuestionIndex < AppState.activeExam.questions.length - 1) {
    loadQuestion(AppState.currentQuestionIndex + 1);
  }
}

function markForReview() {
  const q = AppState.activeExam.questions[AppState.currentQuestionIndex];
  if (!AppState.studentAnswers[q.id]) {
    AppState.studentAnswers[q.id] = { answer: null, is_marked: true };
  } else {
    AppState.studentAnswers[q.id].is_marked = !AppState.studentAnswers[q.id].is_marked;
  }
  loadQuestion(AppState.currentQuestionIndex);
  NotificationManager.show("Question review status updated.", "info", 1500);
}

function clearAnswer() {
  const q = AppState.activeExam.questions[AppState.currentQuestionIndex];
  if (AppState.studentAnswers[q.id]) {
    AppState.studentAnswers[q.id].answer = null;
  }
  loadQuestion(AppState.currentQuestionIndex);
  NotificationManager.show("Answer cleared.", "info", 1500);
}

// Auto Save Progress
function autoSaveProgress() {
  if (AppState.activeExam) {
    localStorage.setItem(`exam_draft_${AppState.activeExam.exam_id}`, JSON.stringify({
      answers: AppState.studentAnswers,
      time_remaining: AppState.timeRemainingSeconds
    }));
    NotificationManager.show("Progress auto-saved.", "info", 1200);
  }
}

// Submit Dialog Controls
function openSubmitModal() {
  const modal = document.getElementById('submit-confirm-modal');
  if (modal) modal.classList.add('active');
}

function closeSubmitModal() {
  const modal = document.getElementById('submit-confirm-modal');
  if (modal) modal.classList.remove('active');
}

async function autoSubmitExam() {
  closeSubmitModal();
  if (AppState.timerInterval) clearInterval(AppState.timerInterval);
  if (AppState.autoSaveInterval) clearInterval(AppState.autoSaveInterval);

  showLoading("Evaluating your examination answers...");

  const timeTaken = (AppState.activeExam.duration_minutes * 60) - AppState.timeRemainingSeconds;

  const res = await apiCall('/submit-exam', 'POST', {
    exam_id: AppState.activeExam.exam_id,
    answers: AppState.studentAnswers,
    time_taken: Math.max(0, timeTaken)
  });

  hideLoading();

  if (res.success && res.data) {
    NotificationManager.show("Examination evaluated successfully!", "success");
    renderResultView(res.data);
    showView('result-view');
  } else {
    NotificationManager.show(res.message || "Error evaluating exam.", "error");
  }
}

// Keyboard Navigation
function handleExamKeydown(e) {
  if (AppState.currentView !== 'exam-interface-view') return;

  if (e.key === 'ArrowLeft') prevQuestion();
  else if (e.key === 'ArrowRight') nextQuestion();
  else if (['1', 'a', 'A'].includes(e.key)) {
    const q = AppState.activeExam.questions[AppState.currentQuestionIndex];
    selectOption(q.id, 'A');
  } else if (['2', 'b', 'B'].includes(e.key)) {
    const q = AppState.activeExam.questions[AppState.currentQuestionIndex];
    selectOption(q.id, 'B');
  } else if (['3', 'c', 'C'].includes(e.key)) {
    const q = AppState.activeExam.questions[AppState.currentQuestionIndex];
    selectOption(q.id, 'C');
  } else if (['4', 'd', 'D'].includes(e.key)) {
    const q = AppState.activeExam.questions[AppState.currentQuestionIndex];
    selectOption(q.id, 'D');
  }
}
