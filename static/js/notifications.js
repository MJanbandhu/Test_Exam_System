/* Toast Notification Manager */

const NotificationManager = {
  container: null,

  init() {
    if (!this.container) {
      this.container = document.createElement('div');
      this.container.id = 'toast-container';
      document.body.appendChild(this.container);
    }
  },

  show(message, type = 'info', duration = 3500) {
    this.init();

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;

    let iconClass = 'fa-info-circle';
    if (type === 'success') iconClass = 'fa-check-circle';
    else if (type === 'warning') iconClass = 'fa-exclamation-triangle';
    else if (type === 'error') iconClass = 'fa-times-circle';

    toast.innerHTML = `
      <i class="fas ${iconClass}"></i>
      <div style="flex: 1; font-size: 0.95rem;">${message}</div>
      <i class="fas fa-times" style="cursor: pointer; opacity: 0.7;" onclick="this.parentElement.remove()"></i>
    `;

    this.container.appendChild(toast);

    setTimeout(() => {
      if (toast.parentElement) {
        toast.style.animation = 'slideOut 0.3s ease-in forwards';
        setTimeout(() => toast.remove(), 300);
      }
    }, duration);
  }
};

// Add slideOut keyframe dynamically
const style = document.createElement('style');
style.innerHTML = `
@keyframes slideOut {
  from { transform: translateX(0); opacity: 1; }
  to { transform: translateX(100%); opacity: 0; }
}`;
document.head.appendChild(style);
