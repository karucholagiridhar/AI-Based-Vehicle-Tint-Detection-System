/**
 * Profile API Service
 * Handles all profile-related API calls
 */

class ProfileService {
    constructor(apiClient) {
        this.api = apiClient;
    }

    /**
     * Get current user profile
     */
    async getProfile() {
        return this.api.get('/profile/get');
    }

    /**
     * Update user profile
     * @param {Object} profileData - { full_name, email, phone, organization }
     */
    async updateProfile(profileData) {
        return this.api.post('/profile/update', profileData);
    }

    /**
     * Change password
     * @param {Object} passwordData - { current_password, new_password, confirm_password }
     */
    async changePassword(passwordData) {
        return this.api.post('/profile/change-password', passwordData);
    }
}

// Export
window.ProfileService = ProfileService;
