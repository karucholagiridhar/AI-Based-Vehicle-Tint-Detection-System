/**
 * Inference API Service
 * Handles tint detection inference calls
 */

class InferenceService {
    constructor(apiClient) {
        this.api = apiClient;
    }

    /**
     * Upload and detect tint from image file
     * @param {File} file - Image file
     * @param {Function} onProgress - Progress callback (0-100)
     */
    async detectFromFile(file, onProgress = null) {
        return this.api.upload('/inference/detect', file, onProgress);
    }

    /**
     * Get inference history
     * @param {Object} params - { limit, offset }
     */
    async getHistory(params = {}) {
        return this.api.get('/inference/history', params);
    }

    /**
     * Get specific test result
     * @param {Number} resultId
     */
    async getResult(resultId) {
        return this.api.get(`/inference/result/${resultId}`);
    }

    /**
     * Delete test result
     * @param {Number} resultId
     */
    async deleteResult(resultId) {
        return this.api.delete(`/inference/result/${resultId}`);
    }
}

// Export
window.InferenceService = InferenceService;
