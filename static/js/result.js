/* Results Evaluation, Chart Visualization & History Manager */

let pieChartInstance = null;
let barChartInstance = null;

async function renderResultView(resultPayload) {
  const exam = resultPayload.exam;
  const cert = resultPayload.certificate;

  // Header Details
  document.getElementById('res-student-name').textContent = exam.student_name;
  document.getElementById('res-subject').textContent = exam.subject;
  document.getElementById('res-difficulty').textContent = exam.difficulty;
  document.getElementById('res-date').textContent = String(exam.date).slice(0, 16);

  const mins = Math.floor(exam.time_taken / 60);
  const secs = exam.time_taken % 60;
  document.getElementById('res-time-taken').textContent = `${mins}m ${secs}s`;

  // Score metrics
  document.getElementById('res-score').textContent = `${exam.score} / ${exam.total_questions}`;
  document.getElementById('res-percentage').textContent = `${exam.percentage.toFixed(1)}%`;
  
  const gradeBadge = document.getElementById('res-grade');
  gradeBadge.textContent = exam.grade;

  const statusBadge = document.getElementById('res-status');
  statusBadge.textContent = exam.status;
  if (exam.status === 'Pass') {
    statusBadge.className = 'badge bg-success';
    document.getElementById('res-certificate-btn-container').style.display = 'inline-block';
  } else {
    statusBadge.className = 'badge bg-danger';
    document.getElementById('res-certificate-btn-container').style.display = 'none';
  }

  // Setup Download Links
  const resultPdfBtn = document.getElementById('download-result-pdf-btn');
  if (resultPdfBtn) resultPdfBtn.href = `/download-result/${exam.id}`;

  const certPdfBtn = document.getElementById('download-cert-pdf-btn');
  if (certPdfBtn) certPdfBtn.href = `/download-certificate/${exam.id}`;

  // Render Charts
  renderCharts(exam);

  // Load Answer Review
  await loadAnswerReview(exam.id);
}

// Render Chart.js
function renderCharts(exam) {
  const pieCtx = document.getElementById('resultPieChart');
  const barCtx = document.getElementById('resultBarChart');

  if (!pieCtx || !barCtx) return;

  if (pieChartInstance) pieChartInstance.destroy();
  if (barChartInstance) barChartInstance.destroy();

  // Pie Chart
  pieChartInstance = new Chart(pieCtx, {
    type: 'doughnut',
    data: {
      labels: ['Correct', 'Wrong', 'Skipped'],
      datasets: [{
        data: [exam.correct_count, exam.wrong_count, exam.skipped_count],
        backgroundColor: ['#10b981', '#ef4444', '#f59e0b'],
        borderWidth: 0
      }]
    },
    options: {
      responsive: true,
      plugins: {
        legend: { position: 'bottom', labels: { color: AppState.theme === 'dark' ? '#f8fafc' : '#0f172a' } }
      }
    }
  });

  // Bar Chart
  barChartInstance = new Chart(barCtx, {
    type: 'bar',
    data: {
      labels: ['Your Score (%)', 'Passing Limit (50%)', 'Target Benchmark (80%)'],
      datasets: [{
        label: 'Percentage Performance',
        data: [exam.percentage, 50, 80],
        backgroundColor: ['#3b82f6', '#64748b', '#10b981'],
        borderRadius: 8
      }]
    },
    options: {
      responsive: true,
      scales: {
        y: { beginAtZero: true, max: 100, ticks: { color: AppState.theme === 'dark' ? '#94a3b8' : '#475569' } },
        x: { ticks: { color: AppState.theme === 'dark' ? '#94a3b8' : '#475569' } }
      },
      plugins: {
        legend: { display: false }
      }
    }
  });
}

// Answer Review Accordion / List
async function loadAnswerReview(examId) {
  const container = document.getElementById('answer-review-container');
  if (!container) return;
  container.innerHTML = '<div style="text-align:center; padding: 20px;">Loading answer breakdown...</div>';

  const res = await apiCall(`/result/${examId}`);
  if (!res.success || !res.data) return;

  const { questions, answers } = res.data;
  container.innerHTML = '';

  questions.forEach((q, idx) => {
    const qAns = answers[q.id] || {};
    const stdAns = qAns.student_answer || 'Skipped';
    const corrAns = q.correct_answer;
    
    let statusClass = 'skipped';
    let statusText = 'Skipped';
    let statusBg = 'border-left: 5px solid var(--color-warning);';

    if (stdAns === corrAns) {
      statusClass = 'correct';
      statusText = 'Correct';
      statusBg = 'border-left: 5px solid var(--color-success);';
    } else if (stdAns !== 'Skipped') {
      statusClass = 'wrong';
      statusText = 'Incorrect';
      statusBg = 'border-left: 5px solid var(--color-danger);';
    }

    const card = document.createElement('div');
    card.className = 'glass-card';
    card.style.cssText = `${statusBg} margin-bottom: 16px; padding: 20px;`;
    
    card.innerHTML = `
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
        <span style="font-weight: 700; font-size: 1.05rem;">Q${idx + 1}. ${q.question}</span>
        <span class="badge ${statusClass}" style="padding: 4px 12px; border-radius: 8px; font-weight: 700;">${statusText}</span>
      </div>
      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; font-size: 0.95rem; margin-bottom: 12px;">
        <div><b>Option A:</b> ${q.option_a}</div>
        <div><b>Option B:</b> ${q.option_b}</div>
        <div><b>Option C:</b> ${q.option_c}</div>
        <div><b>Option D:</b> ${q.option_d}</div>
      </div>
      <div style="background: rgba(0,0,0,0.2); padding: 12px 16px; border-radius: 12px; font-size: 0.9rem;">
        <div><b>Your Answer:</b> <span style="color: ${stdAns === corrAns ? 'var(--color-success)' : (stdAns === 'Skipped' ? 'var(--color-warning)' : 'var(--color-danger)')}">${stdAns}</span></div>
        <div><b>Correct Answer:</b> <span style="color: var(--color-success); font-weight:700;">${corrAns}</span></div>
        <div style="margin-top: 6px; color: var(--text-secondary);"><b>Explanation:</b> ${q.explanation}</div>
      </div>
    `;
    container.appendChild(card);
  });
}

// Certificate Popup Modal
async function openCertificateModal() {
  if (!AppState.activeExam) return;
  showLoading("Fetching official Certificate data...");
  const res = await apiCall(`/certificate/${AppState.activeExam.exam_id}`);
  hideLoading();

  if (res.success && res.data) {
    const cert = res.data.certificate;
    const exam = res.data.exam;

    document.getElementById('cert-modal-name').textContent = exam.student_name;
    document.getElementById('cert-modal-subject').textContent = exam.subject;
    document.getElementById('cert-modal-grade').textContent = exam.grade;
    document.getElementById('cert-modal-score').textContent = `${exam.percentage.toFixed(1)}%`;
    document.getElementById('cert-modal-id').textContent = cert ? cert.certificate_id : 'CERT-2026-PENDING';
    document.getElementById('cert-modal-date').textContent = String(exam.date).slice(0, 10);

    const modal = document.getElementById('certificate-preview-modal');
    if (modal) modal.classList.add('active');
  } else {
    NotificationManager.show(res.message || "Certificate not available.", "error");
  }
}

function closeCertificateModal() {
  const modal = document.getElementById('certificate-preview-modal');
  if (modal) modal.classList.remove('active');
}

// History List Manager
async function loadHistoryList() {
  const searchInput = document.getElementById('history-search-input');
  const subjectFilter = document.getElementById('history-subject-filter');
  const statusFilter = document.getElementById('history-status-filter');

  const search = searchInput ? searchInput.value.trim() : '';
  const subject = subjectFilter ? subjectFilter.value.trim() : '';
  const status = statusFilter ? statusFilter.value.trim() : '';

  const endpoint = `/history?search=${encodeURIComponent(search)}&subject=${encodeURIComponent(subject)}&status=${encodeURIComponent(status)}`;
  const res = await apiCall(endpoint);

  const container = document.getElementById('history-table-body');
  if (!container) return;
  container.innerHTML = '';

  if (!res.success || !res.data || res.data.history.length === 0) {
    container.innerHTML = '<tr><td colspan="8" style="text-align:center; padding: 30px; color: var(--text-muted);">No examination history records found.</td></tr>';
    return;
  }

  res.data.history.forEach((h, idx) => {
    const tr = document.createElement('tr');
    const statusColor = h.status === 'Pass' ? 'var(--color-success)' : 'var(--color-danger)';

    tr.innerHTML = `
      <td>${idx + 1}</td>
      <td><b>${h.student_name}</b></td>
      <td>${h.subject}</td>
      <td>${h.difficulty}</td>
      <td>${h.percentage.toFixed(1)}% (${h.grade})</td>
      <td><span style="color: ${statusColor}; font-weight:700;">${h.status}</span></td>
      <td>${String(h.date).slice(0, 10)}</td>
      <td>
        <a href="/download-result/${h.id}" class="btn btn-secondary" style="padding: 4px 10px; font-size: 0.8rem;" title="Download Result PDF"><i class="fas fa-file-pdf"></i></a>
        ${h.status === 'Pass' ? `<a href="/download-certificate/${h.id}" class="btn btn-primary" style="padding: 4px 10px; font-size: 0.8rem;" title="Download Certificate PDF"><i class="fas fa-award"></i></a>` : ''}
        <button onclick="deleteHistoryRecord('${h.id}')" class="btn btn-danger" style="padding: 4px 10px; font-size: 0.8rem;" title="Delete Record"><i class="fas fa-trash"></i></button>
      </td>
    `;
    container.appendChild(tr);
  });
}

async function deleteHistoryRecord(examId) {
  if (!confirm("Are you sure you want to delete this examination record?")) return;
  const res = await apiCall(`/history/${examId}`, 'DELETE');
  if (res.success) {
    NotificationManager.show("Record deleted.", "success");
    loadHistoryList();
  } else {
    NotificationManager.show("Failed to delete record.", "error");
  }
}

// Reset Application Data
function resetApplicationData() {
  if (!confirm("WARNING: This will clear local browser cache settings. Continue?")) return;
  localStorage.clear();
  NotificationManager.show("Application settings reset. Reloading...", "info");
  setTimeout(() => location.reload(), 1000);
}
