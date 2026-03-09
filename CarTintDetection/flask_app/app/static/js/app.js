/**
 * Main Application Initialization
 * Sets up global app object and initializes core components
 */

// Wait for DOM to be ready
document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
});

/**
 * Initialize application
 */
function initializeApp() {
    // Create global App object
    window.App = {
        // API clients
        apiClient: new APIClient('/api'),
        
        // Services
        profile: null,
        inference: null,
        
        // UI Components
        toast: null,
        modal: null,
        loader: null,
        
        // State
        user: null,
        
        // Initialize
        init() {
            // Initialize services
            this.profile = new ProfileService(this.apiClient);
            this.inference = new InferenceService(this.apiClient);
            
            // Initialize UI components
            this.toast = new Toast({
                position: 'top-right',
                duration: 4000,
                maxToasts: 3
            });
            
            this.modal = new Modal();
            this.loader = new Loader();
            
            // Setup global error handler
            this.setupErrorHandler();
            
            // Setup AJAX error handler
            this.setupAjaxErrorHandler();
        },
        
        /**
         * Setup global error handler
         */
        setupErrorHandler() {
            window.addEventListener('error', (event) => {
                console.error('Global error:', event.error);
                // Don't show toast for every error, just log
            });
            
            window.addEventListener('unhandledrejection', (event) => {
                console.error('Unhandled promise rejection:', event.reason);
                
                // Show toast for API errors
                if (event.reason instanceof APIError) {
                    this.handleAPIError(event.reason);
                }
            });
        },
        
        /**
         * Handle API errors globally
         */
        handleAPIError(error) {
            console.error('API Error:', error);
            
            if (error.isUnauthorized()) {
                this.toast.error('Session expired. Please login again.');
                setTimeout(() => {
                    window.location.href = '/auth/login';
                }, 2000);
            } else if (error.isNetworkError()) {
                this.toast.error('Network error. Please check your connection.');
            } else if (error.isServerError()) {
                this.toast.error('Server error. Please try again later.');
            } else {
                this.toast.error(error.message || 'An error occurred');
            }
        },
        
        /**
         * Setup AJAX error handler for fetch
         */
        setupAjaxErrorHandler() {
            const originalFetch = window.fetch;
            window.fetch = async (...args) => {
                try {
                    const response = await originalFetch(...args);
                    return response;
                } catch (error) {
                    console.error('Fetch error:', error);
                    throw error;
                }
            };
        },
        
        /**
         * Show loading overlay
         */
        showLoading(message = 'Loading...') {
            this.loader.showOverlay(message);
        },
        
        /**
         * Hide loading overlay
         */
        hideLoading() {
            this.loader.hideOverlay();
        },
        
        /**
         * Confirm action
         */
        confirm(message, onConfirm, options = {}) {
            this.modal.confirm(message, onConfirm, options);
        },
        
        /**
         * Alert
         */
        alert(message, options = {}) {
            this.modal.alert(message, options);
        }
    };
    
    // Initialize the app
    window.App.init();
}

/**
 * Helper function to format dates
 */
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

/**
 * Helper function to format file size
 */
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
}

/**
 * Helper function to debounce
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Helper function to throttle
 */
function throttle(func, limit) {
    let inThrottle;
    return function(...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// Export helpers
window.formatDate = formatDate;
window.formatFileSize = formatFileSize;
window.debounce = debounce;
window.throttle = throttle;
