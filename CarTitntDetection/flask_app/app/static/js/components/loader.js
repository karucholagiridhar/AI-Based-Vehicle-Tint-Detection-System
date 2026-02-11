/**
 * Loading Component
 * Manages loading states, spinners, and skeleton loaders
 */

class Loader {
    constructor() {
        this.activeLoaders = new Set();
    }

    /**
     * Show button loading state
     */
    button(buttonElement, loadingText = 'Loading...') {
        if (!buttonElement) return null;

        const originalText = buttonElement.innerHTML;
        const originalDisabled = buttonElement.disabled;

        buttonElement.disabled = true;
        buttonElement.innerHTML = `
            <span class="spinner spinner-sm"></span>
            <span>${loadingText}</span>
        `;

        // Return restore function
        return () => {
            buttonElement.disabled = originalDisabled;
            buttonElement.innerHTML = originalText;
        };
    }

    /**
     * Show inline spinner
     */
    show(containerId) {
        const container = document.getElementById(containerId);
        if (!container) return;

        container.innerHTML = `
            <div class="loading-spinner">
                <div class="spinner"></div>
                <p class="loading-text">Loading...</p>
            </div>
        `;

        this.activeLoaders.add(containerId);
    }

    /**
     * Hide loader
     */
    hide(containerId) {
        this.activeLoaders.delete(containerId);
    }

    /**
     * Show full-page overlay loader
     */
    showOverlay(message = 'Loading...') {
        let overlay = document.getElementById('app-loader-overlay');
        
        if (!overlay) {
            overlay = document.createElement('div');
            overlay.id = 'app-loader-overlay';
            overlay.className = 'loader-overlay';
            overlay.innerHTML = `
                <div class="loader-content">
                    <div class="spinner spinner-lg"></div>
                    <p class="loader-message">${message}</p>
                </div>
            `;
            document.body.appendChild(overlay);
        }

        overlay.classList.add('show');
        document.body.style.overflow = 'hidden';
    }

    /**
     * Hide overlay loader
     */
    hideOverlay() {
        const overlay = document.getElementById('app-loader-overlay');
        if (overlay) {
            overlay.classList.remove('show');
            document.body.style.overflow = '';
        }
    }

    /**
     * Show skeleton loader
     */
    skeleton(containerId, type = 'card', count = 1) {
        const container = document.getElementById(containerId);
        if (!container) return;

        const skeletons = Array(count).fill(null).map(() => this.getSkeletonTemplate(type));
        container.innerHTML = skeletons.join('');
    }

    /**
     * Get skeleton template by type
     */
    getSkeletonTemplate(type) {
        const templates = {
            card: `
                <div class="skeleton-card">
                    <div class="skeleton skeleton-image"></div>
                    <div class="skeleton skeleton-title"></div>
                    <div class="skeleton skeleton-text"></div>
                    <div class="skeleton skeleton-text" style="width: 60%;"></div>
                </div>
            `,
            table: `
                <div class="skeleton-table">
                    ${Array(5).fill(`
                        <div class="skeleton-row">
                            <div class="skeleton skeleton-cell"></div>
                            <div class="skeleton skeleton-cell"></div>
                            <div class="skeleton skeleton-cell"></div>
                        </div>
                    `).join('')}
                </div>
            `,
            list: `
                <div class="skeleton-list">
                    ${Array(5).fill(`
                        <div class="skeleton-item">
                            <div class="skeleton skeleton-circle"></div>
                            <div class="skeleton skeleton-text"></div>
                        </div>
                    `).join('')}
                </div>
            `
        };

        return templates[type] || templates.card;
    }

    /**
     * Progress bar
     */
    progress(containerId, percent = 0) {
        const container = document.getElementById(containerId);
        if (!container) return;

        let progressBar = container.querySelector('.progress-bar');
        
        if (!progressBar) {
            container.innerHTML = `
                <div class="progress">
                    <div class="progress-bar" role="progressbar" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100">
                        <span class="progress-text">0%</span>
                    </div>
                </div>
            `;
            progressBar = container.querySelector('.progress-bar');
        }

        const clampedPercent = Math.min(100, Math.max(0, percent));
        progressBar.style.width = `${clampedPercent}%`;
        progressBar.setAttribute('aria-valuenow', clampedPercent);
        progressBar.querySelector('.progress-text').textContent = `${Math.round(clampedPercent)}%`;
    }
}

// Export
window.Loader = Loader;
