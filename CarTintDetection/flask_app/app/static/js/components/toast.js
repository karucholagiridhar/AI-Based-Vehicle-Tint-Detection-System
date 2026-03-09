/**
 * Toast Notification Component
 * Displays success, error, warning, and info messages
 */

class Toast {
    constructor(options = {}) {
        this.container = null;
        this.queue = [];
        this.activeToasts = new Set();
        this.maxToasts = options.maxToasts || 3;
        this.defaultDuration = options.duration || 4000;
        this.position = options.position || 'top-right';
        
        this.init();
    }

    init() {
        // Create toast container
        this.container = document.createElement('div');
        this.container.className = `toast-container toast-${this.position}`;
        this.container.setAttribute('aria-live', 'polite');
        this.container.setAttribute('aria-atomic', 'true');
        document.body.appendChild(this.container);
    }

    /**
     * Show success toast
     */
    success(message, duration = null) {
        return this.show(message, 'success', duration);
    }

    /**
     * Show error toast
     */
    error(message, duration = null) {
        return this.show(message, 'error', duration);
    }

    /**
     * Show warning toast
     */
    warning(message, duration = null) {
        return this.show(message, 'warning', duration);
    }

    /**
     * Show info toast
     */
    info(message, duration = null) {
        return this.show(message, 'info', duration);
    }

    /**
     * Generic show method
     */
    show(message, type = 'info', duration = null) {
        const toast = this.createToast(message, type);
        
        // If max toasts reached, queue it
        if (this.activeToasts.size >= this.maxToasts) {
            this.queue.push({ message, type, duration });
            return toast.id;
        }

        // Add to DOM
        this.container.appendChild(toast.element);
        this.activeToasts.add(toast.id);

        // Trigger animation
        requestAnimationFrame(() => {
            toast.element.classList.add('toast-show');
        });

        // Auto-dismiss
        const timeoutDuration = duration !== null ? duration : this.defaultDuration;
        if (timeoutDuration > 0) {
            toast.timeout = setTimeout(() => {
                this.dismiss(toast.id);
            }, timeoutDuration);
        }

        return toast.id;
    }

    /**
     * Create toast element
     */
    createToast(message, type) {
        const id = `toast-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
        
        const element = document.createElement('div');
        element.className = `toast toast-${type}`;
        element.id = id;
        element.setAttribute('role', 'alert');

        const icon = this.getIcon(type);
        
        element.innerHTML = `
            <div class="toast-icon">${icon}</div>
            <div class="toast-content">
                <div class="toast-message">${this.escapeHtml(message)}</div>
            </div>
            <button class="toast-close" aria-label="Close" onclick="window.App.toast.dismiss('${id}')">
                ×
            </button>
        `;

        return { id, element, timeout: null };
    }

    /**
     * Dismiss toast
     */
    dismiss(toastId) {
        const toast = document.getElementById(toastId);
        if (!toast) return;

        // Remove animation
        toast.classList.remove('toast-show');
        toast.classList.add('toast-hide');

        // Remove from DOM after animation
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
            this.activeToasts.delete(toastId);

            // Show next queued toast
            if (this.queue.length > 0) {
                const next = this.queue.shift();
                this.show(next.message, next.type, next.duration);
            }
        }, 300);
    }

    /**
     * Dismiss all toasts
     */
    dismissAll() {
        this.activeToasts.forEach(id => this.dismiss(id));
        this.queue = [];
    }

    /**
     * Get icon for toast type
     */
    getIcon(type) {
        const icons = {
            success: '✓',
            error: '✕',
            warning: '⚠',
            info: 'ℹ'
        };
        return icons[type] || icons.info;
    }

    /**
     * Escape HTML to prevent XSS
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Export
window.Toast = Toast;
