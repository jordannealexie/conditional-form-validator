/**
 * FormRenderer: Dynamically generates and manages forms from JSON templates.
 * Uses the project's design system CSS classes for consistent styling.
 */
class FormRenderer {
    constructor(containerId, options = {}) {
        this.container = document.getElementById(containerId);
        this.fields = [];
        this.formData = {};
        this.onChanged = options.onChanged || null;
        this.onValidated = options.onValidated || null;
        this.uploadedFiles = {}; // Store file tokens
        this.inputValidationTimeout = null; // For debounced validation
    }

    render(fields) {
        this.fields = fields;
        this.container.innerHTML = '';

        const form = document.createElement('form');
        form.id = 'dynamic-form';
        form.className = 'form-container';

        fields.forEach(field => {
            const fieldWrapper = this.createFieldElement(field);
            form.appendChild(fieldWrapper);
        });

        // Add submit button - REMOVED: Buttons are now handled in the parent page (form-fill.html) to prevent duplication and improve layout control.
        // const submitSection = document.createElement('div');
        // submitSection.className = 'form-actions';
        // ...
        // form.appendChild(submitSection);

        // Form submit handler
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleSubmit();
        });

        this.container.appendChild(form);
        this.updateVisibility();
    }

    createFieldElement(field) {
        const wrapper = document.createElement('div');
        wrapper.id = `wrapper-${field.id}`;
        wrapper.className = 'field-wrapper';
        
        // Add special classes for specific field types
        if (field.type === 'currency') {
            wrapper.classList.add('field-currency-wrapper');
        } else if (field.type === 'percentage') {
            wrapper.classList.add('field-percentage-wrapper');  
        } else if (field.type === 'phone') {
            wrapper.classList.add('field-phone');
        }

        const label = document.createElement('label');
        label.htmlFor = field.id;
        label.textContent = field.label + (field.required ? ' *' : '');
        wrapper.appendChild(label);

        let input;

        if (field.type === 'select') {
            input = document.createElement('select');
            input.id = field.id;
            input.name = field.id;
            input.className = 'form-select';
            if (field.required) input.setAttribute('required', 'true');

            // Add default empty option
            const defaultOption = document.createElement('option');
            defaultOption.value = '';
            defaultOption.textContent = `Select ${field.label}...`;
            input.appendChild(defaultOption);

            field.options.forEach(opt => {
                const option = document.createElement('option');
                option.value = opt;
                option.textContent = opt;
                input.appendChild(option);
            });
        } else if (field.type === 'textarea') {
            input = document.createElement('textarea');
            input.id = field.id;
            input.name = field.id;
            input.className = 'form-textarea';
            if (field.placeholder) input.placeholder = field.placeholder;
            if (field.rows) input.rows = field.rows;
            if (field.required) input.setAttribute('required', 'true');
        } else if (field.type === 'checkbox') {
            input = document.createElement('input');
            input.type = 'checkbox';
            input.id = field.id;
            input.name = field.id;
            input.className = 'form-checkbox';

            // Reset label for checkbox - checkbox comes before text
            const checkboxWrapper = document.createElement('div');
            checkboxWrapper.className = 'form-group-inline';
            checkboxWrapper.appendChild(input);

            const checkboxLabel = document.createElement('label');
            checkboxLabel.htmlFor = field.id;
            checkboxLabel.textContent = field.label + (field.required ? ' *' : '');
            checkboxWrapper.appendChild(checkboxLabel);

            wrapper.innerHTML = ''; // Clear wrapper
            wrapper.appendChild(checkboxWrapper);
            input = checkboxWrapper; // Reference for event listeners
        } else if (field.type === 'file') {
            input = document.createElement('div');
            input.className = 'file-upload-wrapper';
            input.id = `file-wrapper-${field.id}`;

            const fileInput = document.createElement('input');
            fileInput.type = 'file';
            fileInput.id = field.id;
            fileInput.name = field.id;
            fileInput.className = 'form-file';
            if (field.accept) fileInput.accept = field.accept;
            if (field.required) fileInput.setAttribute('required', 'true');

            // Hidden input to store the token
            const tokenInput = document.createElement('input');
            tokenInput.type = 'hidden';
            tokenInput.id = `${field.id}_token`;
            tokenInput.name = field.id;

            const uploadStatus = document.createElement('div');
            uploadStatus.id = `${field.id}_status`;
            uploadStatus.className = 'upload-status';

            input.appendChild(fileInput);
            input.appendChild(tokenInput);
            input.appendChild(uploadStatus);

            // File upload handler
            fileInput.addEventListener('change', async (e) => {
                await this.handleFileUpload(field, e.target.files[0]);
            });
        } else {
            input = document.createElement('input');
            
            // Map field types to HTML input types
            if (field.type === 'phone') {
                input.type = 'tel';
            } else if (field.type === 'currency' || field.type === 'percentage') {
                input.type = 'number';
                if (field.type === 'currency') {
                    input.step = '0.01';
                    input.min = '0';
                } else if (field.type === 'percentage') {
                    input.min = '0';
                    input.max = '100';
                    input.step = '1';
                }
            } else if (field.type === 'boolean') {
                input.type = 'checkbox';
            } else {
                input.type = field.type || 'text';
            }
            
            input.id = field.id;
            input.name = field.id;
            input.className = 'form-input';
            if (field.placeholder) input.placeholder = field.placeholder;
            if (field.required) input.setAttribute('required', 'true');
        }

        // Add validation attributes
        if (field.validation) {
            if (field.validation.minLength) input.minLength = field.validation.minLength;
            if (field.validation.maxLength) input.maxLength = field.validation.maxLength;
            if (field.validation.minimum) input.min = field.validation.minimum;
            if (field.validation.maximum) input.max = field.validation.maximum;
            if (field.validation.pattern) input.pattern = field.validation.pattern;
        }

        // Event listeners for non-checkbox, non-file inputs
        if (field.type !== 'checkbox' && field.type !== 'file') {
            input.addEventListener('change', () => {
                this.handleInputChange(field.id);
                this.validateField(field);
            });
            input.addEventListener('input', () => {
                this.handleInputChange(field.id);
                // Add slight delay for input validation to avoid excessive validation
                clearTimeout(this.inputValidationTimeout);
                this.inputValidationTimeout = setTimeout(() => {
                    this.validateField(field);
                }, 300);
            });
        } else {
            input.addEventListener('change', () => {
                this.handleInputChange(field.id);
                this.validateField(field);
            });
        }

        if (field.type !== 'checkbox') {
            wrapper.appendChild(input);
        }

        // Error message placeholder
        const errorDiv = document.createElement('div');
        errorDiv.className = 'field-error';
        errorDiv.id = `error-${field.id}`;
        errorDiv.style.display = 'none';
        wrapper.appendChild(errorDiv);

        // Help text
        if (field.description && field.type !== 'checkbox') {
            const helpText = document.createElement('small');
            helpText.className = 'form-help';
            helpText.textContent = field.description;
            wrapper.appendChild(helpText);
        }

        return wrapper;
    }

    async handleFileUpload(field, file) {
        if (!file) return;

        const statusEl = document.getElementById(`${field.id}_status`);
        statusEl.innerHTML = '<span>Uploading...</span>';
        statusEl.className = 'upload-status uploading';

        try {
            const formData = new FormData();
            formData.append('file', file);
            formData.append('field_id', field.id);

            const result = await apiUploadFile(formData);

            // Store token
            this.uploadedFiles[field.id] = result.token;
            document.getElementById(`${field.id}_token`).value = result.token;

            statusEl.innerHTML = `
                <span class="upload-success">✓ ${result.original_filename} uploaded</span>
                <button type="button" class="btn btn-sm btn-secondary" 
                    onclick="renderer.removeFile('${field.id}')">Remove</button>
            `;
            statusEl.className = 'upload-status success';

            this.handleInputChange(field.id);
        } catch (error) {
            statusEl.innerHTML = `<span class="upload-error">✗ Upload failed: ${error.message}</span>`;
            statusEl.className = 'upload-status error';
        }
    }

    removeFile(fieldId) {
        delete this.uploadedFiles[fieldId];
        document.getElementById(`${fieldId}_token`).value = '';
        const statusEl = document.getElementById(`${fieldId}_status`);
        statusEl.innerHTML = '';
        statusEl.className = 'upload-status';
        document.getElementById(fieldId).value = '';
        this.handleInputChange(fieldId);
    }

    handleInputChange(fieldId) {
        this.updateFormData();
        this.updateVisibility();
        if (this.onChanged) this.onChanged(this.getData());
    }

    updateFormData() {
        const data = {};
        this.fields.forEach(field => {
            const input = document.getElementById(field.id);
            if (input) {
                if (field.type === 'checkbox' || field.type === 'boolean') {
                    data[field.id] = input.checked;
                } else if (field.type === 'file') {
                    data[field.id] = this.uploadedFiles[field.id] || null;
                } else if (field.type === 'number' || field.type === 'integer' || field.type === 'currency' || field.type === 'percentage') {
                    // Convert to number if not empty
                    const val = input.value;
                    data[field.id] = val === '' ? null : Number(val);
                } else {
                    data[field.id] = input.value;
                }
            }
        });
        this.formData = data;
    }

    updateVisibility() {
        this.fields.forEach(field => {
            const wrapper = document.getElementById(`wrapper-${field.id}`);
            if (wrapper) {
                const isVisible = this.evaluateCondition(field.show_if);
                wrapper.style.display = isVisible ? 'block' : 'none';
                if (!isVisible) {
                    // Clear value when hidden (without triggering change events to prevent infinite loop)
                    const input = document.getElementById(field.id);
                    if (input) {
                        if (field.type === 'checkbox' || field.type === 'boolean') {
                            input.checked = false;
                        } else if (field.type === 'file') {
                            // Clear file field without calling removeFile() to avoid infinite recursion
                            delete this.uploadedFiles[field.id];
                            const tokenInput = document.getElementById(`${field.id}_token`);
                            if (tokenInput) tokenInput.value = '';
                            const statusEl = document.getElementById(`${field.id}_status`);
                            if (statusEl) {
                                statusEl.innerHTML = '';
                                statusEl.className = 'upload-status';
                            }
                            input.value = '';
                        } else {
                            input.value = '';
                        }
                    }
                    // Clear validation errors for hidden fields
                    this.clearFieldError(field.id);
                } else {
                    // Re-validate visible fields to ensure they're properly validated
                    setTimeout(() => {
                        this.validateField(field);
                    }, 100);
                }
            }
        });
    }

    evaluateCondition(condition) {
        if (!condition) return true;
        if (typeof condition === 'boolean') return condition;

        if (condition.all) {
            return condition.all.every(c => this.evaluateCondition(c));
        }
        if (condition.any) {
            return condition.any.some(c => this.evaluateCondition(c));
        }
        if (condition.not) {
            return !this.evaluateCondition(condition.not);
        }

        const { field, operator, value: targetValue } = condition;
        const currentValue = this.formData[field];

        switch (operator) {
            case 'equals': return currentValue == targetValue;
            case 'not_equals': return currentValue != targetValue;
            case 'greater_than': return Number(currentValue) > Number(targetValue);
            case 'less_than': return Number(currentValue) < Number(targetValue);
            case 'greater_or_equal': return Number(currentValue) >= Number(targetValue);
            case 'less_or_equal': return Number(currentValue) <= Number(targetValue);
            case 'in': return Array.isArray(targetValue) && targetValue.includes(currentValue);
            case 'not_in': return Array.isArray(targetValue) && !targetValue.includes(currentValue);
            case 'contains': return currentValue && String(currentValue).includes(targetValue);
            case 'matches': return new RegExp(targetValue).test(currentValue);
            default: return true;
        }
    }

    validateField(field) {
        const input = document.getElementById(field.id);
        if (!input) return;

        const value = this.getFieldValue(field, input);
        const isVisible = this.evaluateCondition(field.show_if);
        
        // Clear existing error first
        this.clearFieldError(field.id);
        
        // Skip validation if field is not visible
        if (!isVisible) return;
        
        // Skip validation if field is not required and empty
        if (!field.required && (value === null || value === '' || value === undefined)) return;
        
        // Required field validation
        if (field.required && (value === null || value === '' || value === undefined)) {
            this.showError(field.id, `${field.label} is required`);
            return;
        }
        
        // Type-specific validation
        const typeError = this.validateFieldType(field, value);
        if (typeError) {
            this.showError(field.id, typeError);
            return;
        }
        
        // Validation rules
        if (field.validation) {
            const ruleError = this.validateFieldRules(field, value);
            if (ruleError) {
                this.showError(field.id, ruleError);
                return;
            }
        }
    }
    
    getFieldValue(field, input) {
        if (!input) return null;
        
        if (field.type === 'checkbox' || field.type === 'boolean') {
            return input.checked;
        } else if (field.type === 'file') {
            return this.uploadedFiles[field.id] || null;
        } else if (field.type === 'number' || field.type === 'currency' || field.type === 'percentage') {
            return input.value === '' ? null : Number(input.value);
        } else {
            return input.value === '' ? null : input.value;
        }
    }
    
    validateFieldType(field, value) {
        if (value === null || value === '' || value === undefined) return null;
        
        switch (field.type) {
            case 'email':
                const emailPattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
                if (!emailPattern.test(value)) {
                    return `${field.label} must be a valid email address`;
                }
                break;
                
            case 'phone':
                const phonePattern = /^(09|\+639)\d{9}$/;
                if (!phonePattern.test(value.toString().trim())) {
                    return `${field.label} must be a valid Philippines phone number (09XXXXXXXXX or +639XXXXXXXXX)`;
                }
                break;
                
            case 'number':
            case 'currency':
            case 'percentage':
                if (isNaN(value) || !isFinite(value)) {
                    return `${field.label} must be a valid number`;
                }
                if (field.type === 'currency' && value < 0) {
                    return `${field.label} cannot be negative`;
                }
                if (field.type === 'percentage' && (value < 0 || value > 100)) {
                    return `${field.label} must be between 0 and 100`;
                }
                break;
                
            case 'select':
                if (field.options && !field.options.includes(value)) {
                    return `${field.label} must be one of the allowed options`;
                }
                break;
                
            case 'date':
                const datePattern = /^\d{4}-\d{2}-\d{2}$/;
                if (!datePattern.test(value)) {
                    return `${field.label} must be a valid date in YYYY-MM-DD format`;
                }
                break;
        }
        
        return null;
    }
    
    validateFieldRules(field, value) {
        const rules = field.validation;
        if (!rules || value === null || value === '' || value === undefined) return null;
        
        // Length validations for string types
        if (['text', 'textarea', 'email', 'phone'].includes(field.type) && typeof value === 'string') {
            if (rules.minLength && value.length < rules.minLength) {
                return `${field.label} must be at least ${rules.minLength} characters long`;
            }
            if (rules.maxLength && value.length > rules.maxLength) {
                return `${field.label} must be no more than ${rules.maxLength} characters long`;
            }
        }
        
        // Numeric validations
        if (['number', 'currency', 'percentage'].includes(field.type) && typeof value === 'number') {
            if (rules.minimum !== undefined && value < rules.minimum) {
                return `${field.label} must be at least ${rules.minimum}`;
            }
            if (rules.maximum !== undefined && value > rules.maximum) {
                return `${field.label} must be no more than ${rules.maximum}`;
            }
        }
        
        // Pattern validation for string fields
        if (rules.pattern && ['text', 'email', 'phone'].includes(field.type) && typeof value === 'string') {
            const pattern = new RegExp(rules.pattern);
            if (!pattern.test(value)) {
                return `${field.label} format is not valid`;
            }
        }
        
        return null;
    }
    
    clearFieldError(fieldId) {
        const errorDiv = document.getElementById(`error-${fieldId}`);
        const wrapper = document.getElementById(`wrapper-${fieldId}`);
        if (errorDiv) {
            errorDiv.style.display = 'none';
            errorDiv.textContent = '';
        }
        if (wrapper) {
            wrapper.classList.remove('has-error');
        }
    }

    showError(fieldId, message) {
        const errorDiv = document.getElementById(`error-${fieldId}`);
        const wrapper = document.getElementById(`wrapper-${fieldId}`);
        if (errorDiv && wrapper) {
            errorDiv.textContent = message;
            errorDiv.style.display = 'block';
            wrapper.classList.add('has-error');
        }
    }

    clearErrors() {
        document.querySelectorAll('.field-error').forEach(el => {
            el.style.display = 'none';
        });
        document.querySelectorAll('.field-wrapper').forEach(el => {
            el.classList.remove('has-error');
        });
    }

    getData() {
        this.updateFormData();
        return {
            form_data: this.formData,
            file_tokens: Object.values(this.uploadedFiles)
        };
    }

    async validate() {
        this.clearErrors();
        
        // Run client-side validation first
        let hasClientErrors = false;
        this.fields.forEach(field => {
            const isVisible = this.evaluateCondition(field.show_if);
            if (isVisible) {
                this.validateField(field);
                const errorDiv = document.getElementById(`error-${field.id}`);
                if (errorDiv && errorDiv.style.display !== 'none') {
                    hasClientErrors = true;
                }
            }
        });
        
        // If client-side validation fails, return early
        if (hasClientErrors) {
            return { is_valid: false, errors: [{ field: '__client__', message: 'Please fix the validation errors' }] };
        }
        
        // Run server-side validation
        const data = this.getData();

        try {
            const result = await apiValidateSubmission(
                window.currentTemplateId,
                data.form_data
            );

            if (!result.is_valid && result.errors) {
                result.errors.forEach(error => {
                    this.showError(error.field, error.message);
                });
            }

            return result;
        } catch (error) {
            console.error('Validation error:', error);
            return { is_valid: false, errors: [{ field: '__global__', message: error.message }] };
        }
    }

    async handleSubmit() {
        const validationResult = await this.validate();

        if (validationResult.is_valid) {
            try {
                const data = this.getData();
                const submitData = {
                    template_id: window.currentTemplateId,
                    status: 'submitted',
                    data_json: data.form_data,
                    file_tokens: Object.values(this.uploadedFiles)
                };

                const result = await apiSubmitForm(submitData);
                showToast('Application submitted successfully!', 'success');

                // Redirect to submissions page after a delay
                setTimeout(() => {
                    window.location.href = 'submissions.html';
                }, 2000);

            } catch (error) {
                showToast(error.message || 'Error submitting application', 'error');
            }
        } else {
            showToast('Please fix the validation errors before submitting', 'error');
        }
    }

    async saveDraft() {
        try {
            const data = this.getData();
            const submitData = {
                template_id: window.currentTemplateId,
                status: 'draft',
                data_json: data.form_data,
                file_tokens: Object.values(this.uploadedFiles)
            };

            const result = await apiSubmitForm(submitData);
            showToast('Draft saved successfully!', 'success');

        } catch (error) {
            showToast(error.message || 'Error saving draft', 'error');
        }
    }

    setData(data) {
        // Populate form with existing data (for editing drafts)
        if (data) {
            Object.keys(data).forEach(key => {
                const input = document.getElementById(key);
                if (input) {
                    if (input.type === 'checkbox') {
                        input.checked = data[key];
                    } else if (input.type === 'file') {
                        // File inputs can't be pre-populated
                    } else {
                        input.value = data[key] !== null && data[key] !== undefined ? data[key] : '';
                    }
                }
            });
            this.updateFormData();
            this.updateVisibility();
        }
    }
}

