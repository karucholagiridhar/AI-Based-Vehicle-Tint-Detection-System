/**
 * Modal Component
 * Reusable modal dialog system
 */

class Modal {
    constructor() {
        this.activeModals = new Map();
        this.setupEventListeners();
    }

    /**
     * Setup global event listeners
     */
    setupEventListeners() {
        // Close modal on ESC key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                const lastModal = Array.from(this.activeModals.keys()).pop();
                if (lastModal) {
                    this.close(lastModal);
                }
            }
        });

        // Close modal on overlay click
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal-overlay')) {
                const modalId = e.target.id;
                if (modalId) {
                    this.close(modalId);
                }
            }
        });
    }

    /**
     * Open modal by ID
     */
    open(modalId, options = {}) {
        const modal = document.getElementById(modalId);
        if (!modal) {
            console.error(`Modal ${modalId} not found`);
            return;
        }

        // Add to active modals
        this.activeModals.set(modalId, options);

        // Show modal
        modal.classList.add('show');
        document.body.style.overflow = 'hidden'; // Prevent background scroll

        // Focus first input if exists
        if (options.autoFocus !== false) {
            const firstInput = modal.querySelector('input, textarea, select');
            if (firstInput) {
                setTimeout(() => firstInput.focus(), 100);
            }
        }

        // Callback
        if (options.onOpen) {
            options.onOpen(modal);
        }
    }

    /**
     * Close modal by ID
     */
    close(modalId, options = {}) {
        const modal = document.getElementById(modalId);
        if (!modal) return;

        // Get stored options
        const modalOptions = this.activeModals.get(modalId) || {};

        // Hide modal
        modal.classList.remove('show');
        this.activeModals.delete(modalId);

        // Restore body scroll if no other modals open
        if (this.activeModals.size === 0) {
            document.body.style.overflow = '';
        }

        // Reset form if exists
        const form = modal.querySelector('form');
        if (form && options.resetForm !== false) {
            form.reset();
        }

        // Callback
        if (modalOptions.onClose) {
            modalOptions.onClose(modal);
        }
        if (options.onClose) {
            options.onClose(modal);
        }
    }

    /**
     * Toggle modal
     */
    toggle(modalId, options = {}) {
        if (this.activeModals.has(modalId)) {
            this.close(modalId, options);
        } else {
            this.open(modalId, options);
        }
    }

    /**
     * Create dynamic modal
     */
    create(config = {}) {
        const id = config.id || `modal-${Date.now()}`;
        const title = config.title || 'Modal';
        const content = config.content || '';
        const buttons = config.buttons || [];

        const modal = document.createElement('div');
        modal.id = id;
        modal.className = 'modal-overlay';
        modal.innerHTML = `
            <div class="modal-dialog" style="max-width: ${config.maxWidth || '500px'};">
                <div class="modal-header">
                    <h2 class="modal-title">${this.escapeHtml(title)}</h2>
                    <button class="modal-close" onclick="window.App.modal.close('${id}')" aria-label="Close">
                        ×
                    </button>
                </div>
                <div class="modal-body">
                    ${content}
                </div>
                ${buttons.length > 0 ? `
                    <div class="modal-footer">
                        ${buttons.map(btn => `
                            <button 
                                class="btn ${btn.className || 'btn-outline'}"
                                onclick="${btn.onClick || ''}"
                            >
                                ${this.escapeHtml(btn.text)}
                            </button>
                        `).join('')}
                    </div>
                ` : ''}
            </div>
        `;

        document.body.appendChild(modal);
        return id;
    }

    /**
     * Confirm dialog
     */
    confirm(message, onConfirm, options = {}) {
        const id = this.create({
            title: options.title || 'Confirm',
            content: `<p>${this.escapeHtml(message)}</p>`,
            maxWidth: options.maxWidth || '400px',
            buttons: [
                {
                    text: options.cancelText || 'Cancel',
                    className: 'btn-outline',
                    onClick: `window.App.modal.close('${id}')`
                },
                {
                    text: options.confirmText || 'Confirm',
                    className: options.confirmClass || 'btn-primary',
                    onClick: `window.App.modal.handleConfirm('${id}')`
                }
            ]
        });

        // Store callback
        this.activeModals.set(id, { ...options, onConfirm });
        this.open(id);
    }

    /**
     * Handle confirm action
     */
    handleConfirm(modalId) {
        const options = this.activeModals.get(modalId);
        if (options && options.onConfirm) {
            options.onConfirm();
        }
        this.close(modalId);
        
        // Remove dynamic modal
        setTimeout(() => {
            const modal = document.getElementById(modalId);
            if (modal) modal.remove();
        }, 300);
    }

    /**
     * Alert dialog
     */
    alert(message, options = {}) {
        const id = this.create({
            title: options.title || 'Alert',
            content: `<p>${this.escapeHtml(message)}</p>`,
            maxWidth: options.maxWidth || '400px',
            buttons: [
                {
                    text: options.okText || 'OK',
                    className: 'btn-primary',
                    onClick: `window.App.modal.close('${id}')`
                }
            ]
        });

        this.open(id, {
            onClose: () => {
                setTimeout(() => {
                    const modal = document.getElementById(id);
                    if (modal) modal.remove();
                }, 300);
            }
        });
    }

    /**
     * Escape HTML
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Export
window.Modal = Modal;
