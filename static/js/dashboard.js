/* Registration, API Setup & Exam Configuration Engine */

// Step 2: Validate Student Name
function handleStudentRegistration() {
  const nameInput = document.getElementById('student-name-input');
  const name = nameInput ? nameInput.value.strip ? nameInput.value.strip() : nameInput.value.trim() : '';

  if (!name) {
    NotificationManager.show("Please enter your full name.", "error");
    return false;
  }
  if (name.length < 3) {
    NotificationManager.show("Name must be at least 3 characters long.", "warning");
    return false;
  }
  if (!/^[a-zA-Z\s]+$/.test(name)) {
    NotificationManager.show("Name can only contain alphabets and spaces.", "error");
    return false;
  }

  AppState.studentName = name;
  localStorage.setItem('student_name', name);
  NotificationManager.show(`Welcome, ${name}! Please select your AI Provider.`, "success");
  showView('provider-select-view');
  return true;
}

// Step 3: Select Provider
function selectProvider(provider) {
  AppState.aiProvider = provider;
  localStorage.setItem('ai_provider', provider);

  document.querySelectorAll('.provider-card').forEach(card => {
    card.classList.remove('selected');
  });
  
  const selectedCard = document.getElementById(`provider-card-${provider.toLowerCase().replace(/\s+/g, '')}`);
  if (selectedCard) selectedCard.classList.add('selected');

  // Update label in API key step
  const keyLabel = document.getElementById('api-key-label');
  if (keyLabel) keyLabel.textContent = `${provider} API Key`;
  
  const keyInput = document.getElementById('api-key-input');
  if (keyInput) keyInput.value = '';

  showView('api-config-view');
}

// Step 4 & 5: Connect API Key
async function connectApiKey() {
  const keyInput = document.getElementById('api-key-input');
  const apiKey = keyInput ? keyInput.value.trim() : '';
  const provider = AppState.aiProvider;

  if (!apiKey && provider !== 'Mock') {
    NotificationManager.show(`Please enter your ${provider} API Key.`, "warning");
    return;
  }

  showLoading(`Verifying ${provider} API Key...`);

  const res = await apiCall('/connect-api', 'POST', {
    provider: provider,
    api_key: apiKey
  });

  hideLoading();

  if (res.success) {
    AppState.apiKeyConnected = true;
    NotificationManager.show(res.message, "success");
    updateDashboardUI();
    showView('dashboard-view');
  } else {
    NotificationManager.show(res.message, "error");
  }
}

// Update Dashboard Header Info
function updateDashboardUI() {
  const nameDisplay = document.getElementById('dash-student-name');
  const providerDisplay = document.getElementById('dash-provider');
  const statusDisplay = document.getElementById('dash-status');
  const datetimeDisplay = document.getElementById('dash-datetime');

  if (nameDisplay) nameDisplay.textContent = AppState.studentName;
  if (providerDisplay) providerDisplay.textContent = AppState.aiProvider;
  if (statusDisplay) {
    statusDisplay.textContent = "Connected";
    statusDisplay.style.color = "var(--color-success)";
  }
  if (datetimeDisplay) {
    const now = new Date();
    datetimeDisplay.textContent = now.toLocaleDateString() + ' ' + now.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
  }
}

// Preset Subject Chip Selection
function selectSubjectPreset(subject) {
  document.querySelectorAll('.preset-chip').forEach(chip => chip.classList.remove('active'));
  const activeChip = Array.from(document.querySelectorAll('.preset-chip')).find(c => c.textContent.trim() === subject);
  if (activeChip) activeChip.classList.add('active');

  const customInput = document.getElementById('custom-subject-input');
  if (customInput) customInput.value = subject;
}

// Difficulty Selection
let selectedDifficulty = 'Intermediate';
function selectDifficulty(diff) {
  selectedDifficulty = diff;
  document.querySelectorAll('.difficulty-card').forEach(card => card.classList.remove('selected'));
  const card = document.getElementById(`diff-card-${diff.toLowerCase()}`);
  if (card) card.classList.add('selected');
}

// Start New Exam Generator Request
async function startExamGeneration() {
  const customInput = document.getElementById('custom-subject-input');
  const subject = customInput ? customInput.value.trim() : 'Python';

  if (!subject) {
    NotificationManager.show("Please select or enter an examination subject.", "warning");
    return;
  }

  showLoading(`Generating 30 AI Questions for ${subject} (${selectedDifficulty})...`);

  const res = await apiCall('/generate-exam', 'POST', {
    student_name: AppState.studentName,
    subject: subject,
    difficulty: selectedDifficulty,
    provider: AppState.aiProvider
  });

  hideLoading();

  if (res.success && res.data) {
    AppState.activeExam = res.data;
    AppState.studentAnswers = {};
    AppState.currentQuestionIndex = 0;
    AppState.timeRemainingSeconds = res.data.duration_minutes * 60;
    
    NotificationManager.show("Exam generated successfully! Preparing rules...", "success");
    setupRulesModal(res.data);
  } else {
    NotificationManager.show(res.message || "Failed to generate examination.", "error");
  }
}

function setupRulesModal(examData) {
  const rulesSub = document.getElementById('rules-subject');
  const rulesDiff = document.getElementById('rules-difficulty');
  if (rulesSub) rulesSub.textContent = examData.subject;
  if (rulesDiff) rulesDiff.textContent = examData.difficulty;

  const modal = document.getElementById('exam-rules-modal');
  if (modal) modal.classList.add('active');
}

function confirmStartExam() {
  const modal = document.getElementById('exam-rules-modal');
  if (modal) modal.classList.remove('active');

  showView('exam-interface-view');
  initExamInterface();
}
