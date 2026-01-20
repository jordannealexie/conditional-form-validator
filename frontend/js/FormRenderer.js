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

        // Add submit button
        const submitSection = document.createElement('div');
        submitSection.className = 'form-actions';
        submitSection.innerHTML = `
            <button type="submit" class="btn btn-primary">Submit Application</button>
            <button type="button" class="btn btn-secondary" onclick="renderer.saveDraft()">Save as Draft</button>
        `;
        form.appendChild(submitSection);

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
            input.type = field.type || 'text';
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
            input.addEventListener('change', () => this.handleInputChange(field.id));
            input.addEventListener('input', () => this.handleInputChange(field.id));
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
                if (field.type === 'checkbox') {
                    data[field.id] = input.checked;
                } else if (field.type === 'file') {
                    data[field.id] = this.uploadedFiles[field.id] || null;
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
                    // Clear value when hidden
                    const input = document.getElementById(field.id);
                    if (input) {
                        if (field.type === 'checkbox') {
                            input.checked = false;
                        } else if (field.type === 'file') {
                            this.removeFile(field.id);
                        } else {
                            input.value = '';
                        }
                    }
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
                        input.value = data[key];
                    }
                }
            });
            this.updateFormData();
            this.updateVisibility();
        }
    }
}

