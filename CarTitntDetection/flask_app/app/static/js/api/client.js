/**
 * API Client - Centralized HTTP client for all API calls
 * Handles authentication, error handling, and request/response formatting
 */

class APIClient {
    constructor(baseURL = '/api') {
        this.baseURL = baseURL;
        this.headers = {
            'Content-Type': 'application/json',
        };
    }

    /**
     * Generic request method
     */
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        
        const config = {
            ...options,
            headers: {
                ...this.headers,
                ...options.headers,
            },
        };

        // Add request body if present
        if (options.body && typeof options.body === 'object') {
            config.body = JSON.stringify(options.body);
        }

        try {
            const response = await fetch(url, config);
            
            // Handle HTTP errors
            if (!response.ok) {
                const error = await response.json().catch(() => ({
                    message: response.statusText
                }));
                throw new APIError(error.message || 'Request failed', response.status, error);
            }

            // Parse JSON response
            const data = await response.json();
            return data;

        } catch (error) {
            if (error instanceof APIError) {
                throw error;
            }
            // Network or parsing errors
            throw new APIError(error.message || 'Network error', 0, error);
        }
    }

    /**
     * GET request
     */
    async get(endpoint, params = {}) {
        const queryString = new URLSearchParams(params).toString();
        const url = queryString ? `${endpoint}?${queryString}` : endpoint;
        
        return this.request(url, {
            method: 'GET',
        });
    }

    /**
     * POST request
     */
    async post(endpoint, data = {}) {
        return this.request(endpoint, {
            method: 'POST',
            body: data,
        });
    }

    /**
     * PUT request
     */
    async put(endpoint, data = {}) {
        return this.request(endpoint, {
            method: 'PUT',
            body: data,
        });
    }

    /**
     * DELETE request
     */
    async delete(endpoint) {
        return this.request(endpoint, {
            method: 'DELETE',
        });
    }

    /**
     * Upload file with progress tracking
     */
    async upload(endpoint, file, onProgress = null) {
        const formData = new FormData();
        formData.append('file', file);

        return new Promise((resolve, reject) => {
            const xhr = new XMLHttpRequest();

            // Progress tracking
            if (onProgress) {
                xhr.upload.addEventListener('progress', (e) => {
                    if (e.lengthComputable) {
                        const percentComplete = (e.loaded / e.total) * 100;
                        onProgress(percentComplete);
                    }
                });
            }

            // Success handler
            xhr.addEventListener('load', () => {
                if (xhr.status >= 200 && xhr.status < 300) {
                    try {
                        const data = JSON.parse(xhr.responseText);
                        resolve(data);
                    } catch (e) {
                        reject(new APIError('Invalid JSON response', xhr.status));
                    }
                } else {
                    try {
                        const error = JSON.parse(xhr.responseText);
                        reject(new APIError(error.message || 'Upload failed', xhr.status, error));
                    } catch (e) {
                        reject(new APIError('Upload failed', xhr.status));
                    }
                }
            });

            // Error handler
            xhr.addEventListener('error', () => {
                reject(new APIError('Network error during upload', 0));
            });

            // Send request
            xhr.open('POST', `${this.baseURL}${endpoint}`);
            xhr.send(formData);
        });
    }
}

/**
 * Custom API Error class
 */
class APIError extends Error {
    constructor(message, status, data = null) {
        super(message);
        this.name = 'APIError';
        this.status = status;
        this.data = data;
    }

    isNetworkError() {
        return this.status === 0;
    }

    isClientError() {
        return this.status >= 400 && this.status < 500;
    }

    isServerError() {
        return this.status >= 500;
    }

    isUnauthorized() {
        return this.status === 401;
    }

    isForbidden() {
        return this.status === 403;
    }

    isNotFound() {
        return this.status === 404;
    }
}

// Export for use in other modules
window.APIClient = APIClient;
window.APIError = APIError;
