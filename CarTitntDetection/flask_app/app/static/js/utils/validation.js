/**
 * Form Validation Utilities
 */

const Validators = {
    /**
     * Validate email format
     */
    email(value) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(value);
    },

    /**
     * Validate phone number
     */
    phone(value) {
        const phoneRegex = /^[\+]?[(]?[0-9]{1,4}[)]?[-\s\.]?[(]?[0-9]{1,4}[)]?[-\s\.]?[0-9]{1,9}$/;
        return phoneRegex.test(value.replace(/\s/g, ''));
    },

    /**
     * Validate password strength
     */
    password(value, requirements = {}) {
        const defaults = {
            minLength: 6,
            requireUppercase: false,
            requireLowercase: false,
            requireNumber: false,
            requireSpecial: false
        };

        const config = { ...defaults, ...requirements };
        const errors = [];

        if (value.length < config.minLength) {
            errors.push(`Must be at least ${config.minLength} characters`);
        }

        if (config.requireUppercase && !/[A-Z]/.test(value)) {
            errors.push('Must contain an uppercase letter');
        }

        if (config.requireLowercase && !/[a-z]/.test(value)) {
            errors.push('Must contain a lowercase letter');
        }

        if (config.requireNumber && !/[0-9]/.test(value)) {
            errors.push('Must contain a number');
        }

        if (config.requireSpecial && !/[!@#$%^&*(),.?":{}|<>]/.test(value)) {
            errors.push('Must contain a special character');
        }

        return {
            valid: errors.length === 0,
            errors
        };
    },

    /**
     * Validate required field
     */
    required(value) {
        return value !== null && value !== undefined && value.toString().trim() !== '';
    },

    /**
     * Validate minimum length
     */
    minLength(value, min) {
        return value.length >= min;
    },

    /**
     * Validate maximum length
     */
    maxLength(value, max) {
        return value.length <= max;
    },

    /**
     * Validate number range
     */
    range(value, min, max) {
        const num = parseFloat(value);
        return !isNaN(num) && num >= min && num <= max;
    },

    /**
     * Validate URL format
     */
    url(value) {
        try {
            new URL(value);
            return true;
        } catch {
            return false;
        }
    },

    /**
     * Validate match (e.g., password confirmation)
     */
    match(value1, value2) {
        return value1 === value2;
    }
};

/**
 * Form Validator Class
 */
class FormValidator {
    constructor(formElement) {
        this.form = formElement;
        this.errors = {};
        this.rules = {};
    }

    /**
     * Add validation rule for a field
     */
    addRule(fieldName, validator, errorMessage) {
        if (!this.rules[fieldName]) {
            this.rules[fieldName] = [];
        }
        this.rules[fieldName].push({ validator, errorMessage });
    }

    /**
     * Validate single field
     */
    validateField(fieldName) {
        const field = this.form.elements[fieldName];
        if (!field) return true;

        const value = field.value;
        const fieldRules = this.rules[fieldName] || [];

        // Clear previous errors
        this.clearFieldError(fieldName);

        for (const rule of fieldRules) {
            const isValid = rule.validator(value, field);
            
            if (!isValid) {
                this.setFieldError(fieldName, rule.errorMessage);
                return false;
            }
        }

        return true;
    }

    /**
     * Validate entire form
     */
    validate() {
        this.errors = {};
        let isValid = true;

        for (const fieldName in this.rules) {
            if (!this.validateField(fieldName)) {
                isValid = false;
            }
        }

        return isValid;
    }

    /**
     * Set field error
     */
    setFieldError(fieldName, message) {
        const field = this.form.elements[fieldName];
        if (!field) return;

        this.errors[fieldName] = message;

        // Add error class
        field.classList.add('is-invalid');

        // Show error message
        let errorElement = field.parentElement.querySelector('.form-error');
        if (!errorElement) {
            errorElement = document.createElement('div');
            errorElement.className = 'form-error';
            field.parentElement.appendChild(errorElement);
        }
        errorElement.textContent = message;
    }

    /**
     * Clear field error
     */
    clearFieldError(fieldName) {
        const field = this.form.elements[fieldName];
        if (!field) return;

        delete this.errors[fieldName];
        field.classList.remove('is-invalid');

        const errorElement = field.parentElement.querySelector('.form-error');
        if (errorElement) {
            errorElement.remove();
        }
    }

    /**
     * Clear all errors
     */
    clearErrors() {
        for (const fieldName in this.errors) {
            this.clearFieldError(fieldName);
        }
        this.errors = {};
    }

    /**
     * Setup live validation
     */
    setupLiveValidation() {
        for (const fieldName in this.rules) {
            const field = this.form.elements[fieldName];
            if (!field) continue;

            // Validate on blur
            field.addEventListener('blur', () => {
                this.validateField(fieldName);
            });

            // Clear error on input
            field.addEventListener('input', () => {
                if (this.errors[fieldName]) {
                    this.clearFieldError(fieldName);
                }
            });
        }
    }
}

// Export
window.Validators = Validators;
window.FormValidator = FormValidator;
