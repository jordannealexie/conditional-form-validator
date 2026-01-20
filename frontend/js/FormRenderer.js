/**
 * FormRenderer: Dynamically generates and manages forms from JSON templates.
 */
class FormRenderer {
    constructor(containerId, options = {}) {
        this.container = document.getElementById(containerId);
        this.fields = [];
        this.formData = {};
        this.onChanged = options.onChanged || null;
        this.onValidated = options.onValidated || null;
    }

    render(fields) {
        this.fields = fields;
        this.container.innerHTML = '';

        const form = document.createElement('form');
        form.id = 'dynamic-form';
        form.className = 'space-y-6';

        fields.forEach(field => {
            const fieldWrapper = this.createFieldElement(field);
            form.appendChild(fieldWrapper);
        });

        this.container.appendChild(form);
        this.updateVisibility();
    }

    createFieldElement(field) {
        const wrapper = document.createElement('div');
        wrapper.id = `wrapper-${field.id}`;
        wrapper.className = 'field-wrapper transition-all duration-300 transform';

        const label = document.createElement('label');
        label.className = 'block text-sm font-medium text-gray-700 mb-1';
        label.textContent = field.label + (field.required ? ' *' : '');
        wrapper.appendChild(label);

        let input;

        if (field.type === 'select') {
            input = document.createElement('select');
            input.className = 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 bg-white';
            field.options.forEach(opt => {
                const option = document.createElement('option');
                option.value = opt;
                option.textContent = opt;
                input.appendChild(option);
            });
        } else if (field.type === 'textarea') {
            input = document.createElement('textarea');
            input.className = 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500';
            input.rows = 4;
        } else if (field.type === 'checkbox') {
            input = document.createElement('input');
            input.type = 'checkbox';
            input.className = 'h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded';
            label.className = 'flex items-center space-x-2 text-sm font-medium text-gray-700 mb-1';
            label.prepend(input);
            // Don't append another label for checkbox
        } else if (field.type === 'file') {
            input = document.createElement('input');
            input.type = 'file';
            input.className = 'block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100';
        } else {
            input = document.createElement('input');
            input.type = field.type || 'text';
            input.className = 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500';
        }

        input.id = field.id;
        input.name = field.id;
        if (field.placeholder) input.placeholder = field.placeholder;

        // Event Listeners
        input.addEventListener('change', () => this.handleInputChange(field.id));
        input.addEventListener('input', () => this.handleInputChange(field.id));

        if (field.type !== 'checkbox') {
            wrapper.appendChild(input);
        }

        // Error message placeholder
        const errorDiv = document.createElement('div');
        errorDiv.className = 'field-error text-red-500 text-xs mt-1 hidden';
        errorDiv.id = `error-${field.id}`;
        wrapper.appendChild(errorDiv);

        return wrapper;
    }

    handleInputChange(fieldId) {
        this.updateFormData();
        this.updateVisibility();
        if (this.onChanged) this.onChanged(this.formData);
    }

    updateFormData() {
        const data = {};
        this.fields.forEach(field => {
            const input = document.getElementById(field.id);
            if (input) {
                if (field.type === 'checkbox') {
                    data[field.id] = input.checked;
                } else if (field.type === 'file') {
                    // File handling is usually separate, but we can store the name/info
                    data[field.id] = input.files.length > 0 ? input.files[0].name : null;
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
                if (isVisible) {
                    wrapper.classList.remove('hidden', 'opacity-0', 'scale-95');
                    wrapper.classList.add('block', 'opacity-100', 'scale-100');
                } else {
                    wrapper.classList.add('hidden', 'opacity-0', 'scale-95');
                    wrapper.classList.remove('block', 'opacity-100', 'scale-100');
                }
            }
        });
    }

    evaluateCondition(condition) {
        if (!condition) return True;
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
            case 'contains': return currentValue && currentValue.includes(targetValue);
            case 'matches': return new RegExp(targetValue).test(currentValue);
            default: return true;
        }
    }

    showError(fieldId, message) {
        const errorDiv = document.getElementById(`error-${fieldId}`);
        const wrapper = document.getElementById(`wrapper-${fieldId}`);
        if (errorDiv && wrapper) {
            errorDiv.textContent = message;
            errorDiv.classList.remove('hidden');
            wrapper.querySelector('input, select, textarea').classList.add('border-red-500');
        }
    }

    clearErrors() {
        document.querySelectorAll('.field-error').forEach(el => el.classList.add('hidden'));
        document.querySelectorAll('.field-wrapper input, .field-wrapper select, .field-wrapper textarea').forEach(el => el.classList.remove('border-red-500'));
    }

    getData() {
        this.updateFormData();
        return this.formData;
    }
}
