/**
 * form-fill.js: Controller for the dynamic form application page.
 */

let renderer = null;
let currentTemplate = null;

document.addEventListener('DOMContentLoaded', async () => {
    // 1. Check Authentication
    if (typeof requireAuth === 'function') requireAuth();

    // 2. Extract Template ID from URL
    const urlParams = new URLSearchParams(window.location.search);
    const templateId = urlParams.get('template_id');

    if (!templateId) {
        showToast('No template selected. Returning to dashboard.', 'error');
        setTimeout(() => {
            window.location.href = 'dashboard.html';
        }, 2000);
        return;
    }

    // Store template ID globally for FormRenderer
    window.currentTemplateId = parseInt(templateId);

    // 3. Load User Info
    await loadUserInfo();

    // 4. Load Template and Initialize Renderer
    await loadTemplate(templateId);

    // 5. Setup Buttons
    document.getElementById('submitBtn').addEventListener('click', handleSubmit);
    document.getElementById('saveDraftBtn').addEventListener('click', handleSaveDraft);
    
    // 6. Setup Mobile Menu
    setupMobileMenu();
});

async function loadUserInfo() {
    try {
        const user = await apiGetCurrentUser();
        const fullName = `${user.first_name || ''} ${user.last_name || ''}`.trim() || user.username;
        document.getElementById('userName').textContent = fullName;
        document.getElementById('userRole').textContent = user.user_role || 'User';
    } catch (error) {
        console.error('Failed to load user info:', error);
    }
}

async function loadTemplate(templateId) {
    const container = document.getElementById('renderer-container');

    try {
        currentTemplate = await apiGetTemplate(templateId);

        // Update Page UI
        document.getElementById('formTitle').textContent = currentTemplate.name;
        document.getElementById('formDescription').textContent = currentTemplate.description || 'Please fill out all the required information below.';

        // Show template banner with bank info
        const templateBanner = document.getElementById('templateBanner');
        const bankLogo = document.getElementById('bankLogo');
        const bankBadge = document.getElementById('bankBadge');
        
        templateBanner.style.display = 'flex';
        
        if (currentTemplate.bank) {
            const bankName = currentTemplate.bank.name;
            const bankCode = currentTemplate.bank.code;
            const primaryColor = currentTemplate.bank.primary_color || '#133522';
            
            bankLogo.textContent = bankCode.substring(0, 2).toUpperCase();
            bankLogo.style.background = primaryColor;
            
            bankBadge.textContent = bankName;
            bankBadge.style.background = `${primaryColor}20`;
            bankBadge.style.color = primaryColor;
        } else {
            bankLogo.textContent = 'BK';
            bankLogo.style.background = 'var(--dark-green)';
            bankBadge.textContent = 'Bank';
        }

        // Initialize Renderer
        renderer = new FormRenderer('renderer-container', {
            onChanged: (data) => console.log('Form data changed:', data)
        });

        // Use the fields from the template
        if (currentTemplate.fields && currentTemplate.fields.length > 0) {
            renderer.render(currentTemplate.fields);
        } else {
            // Fallback: render from schema properties
            const fields = generateFieldsFromSchema(currentTemplate.schema_json);
            renderer.render(fields);
        }

    } catch (error) {
        console.error('Failed to load template:', error);
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">⚠️</div>
                <p class="empty-state-title">Error loading form template</p>
                <p>${error.message || 'Please try again later.'}</p>
                <button onclick="window.location.href='dashboard.html'" class="btn btn-primary" style="margin-top: var(--space-md);">
                    Back to Dashboard
                </button>
            </div>
        `;
    }
}

/**
 * Generate field definitions from JSONSchema properties
 */
function generateFieldsFromSchema(schema) {
    if (!schema || !schema.properties) return [];
    
    const fields = [];
    const required = schema.required || [];
    
    Object.keys(schema.properties).forEach((key, index) => {
        const prop = schema.properties[key];
        const field = {
            id: key,
            label: prop.title || key,
            required: required.includes(key),
            type: mapJsonSchemaType(prop.type)
        };
        
        if (prop.enum) {
            field.options = prop.enum;
        }
        
        if (prop.minLength) field.validation = { ...field.validation, minLength: prop.minLength };
        if (prop.maxLength) field.validation = { ...field.validation, maxLength: prop.maxLength };
        if (prop.minimum) field.validation = { ...field.validation, minimum: prop.minimum };
        if (prop.maximum) field.validation = { ...field.validation, maximum: prop.maximum };
        if (prop.pattern) field.validation = { ...field.validation, pattern: prop.pattern };
        
        fields.push(field);
    });
    
    return fields;
}

function mapJsonSchemaType(jsonType) {
    switch (jsonType) {
        case 'string':
            if (schema.format === 'email') return 'email';
            if (schema.format === 'date') return 'date';
            return 'text';
        case 'number':
        case 'integer':
            return 'number';
        case 'boolean':
            return 'checkbox';
        default:
            return 'text';
    }
}

async function handleSubmit() {
    if (!renderer || !currentTemplate) return;

    // Validate first
    const validationResult = await renderer.validate();
    
    if (!validationResult.is_valid) {
        showToast('Please fix the validation errors before submitting', 'error');
        return;
    }

    try {
        const data = renderer.getData();
        const payload = {
            template_id: currentTemplate.id,
            status: 'submitted',
            data_json: data.form_data,
            file_tokens: data.file_tokens
        };

        const result = await apiSubmitForm(payload);
        showToast('Application submitted successfully!', 'success');
        
        // Show success modal
        document.getElementById('successModal').classList.add('active');
        
    } catch (error) {
        console.error('Submission error:', error);
        showToast(error.message || 'Failed to submit application', 'error');
    }
}

async function handleSaveDraft() {
    if (!renderer || !currentTemplate) return;

    try {
        const data = renderer.getData();
        const payload = {
            template_id: currentTemplate.id,
            status: 'draft',
            data_json: data.form_data,
            file_tokens: data.file_tokens
        };

        await apiSubmitForm(payload);
        showToast('Draft saved successfully!', 'success');
        
    } catch (error) {
        console.error('Draft save error:', error);
        showToast(error.message || 'Failed to save draft', 'error');
    }
}

function setupMobileMenu() {
    const menuToggle = document.getElementById('menuToggle');
    const sidebar = document.getElementById('sidebar');
    if (menuToggle && sidebar) {
        menuToggle.addEventListener('click', () => {
            sidebar.classList.toggle('active');
        });
    }
}

