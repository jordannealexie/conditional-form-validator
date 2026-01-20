/**
 * Admin Template Builder Module
 * Handles dragging fields, editing properties, and saving templates to backend
 */

let fields = [];
let selectedFieldId = null;
let dragType = null;
let currentTemplate = null;
let banks = [];

document.addEventListener('DOMContentLoaded', () => {
    if (typeof requireAuth === 'function') requireAuth();
    loadUserInfo();
    loadBanks();
    loadTemplates(); // Load existing templates
    setupMobileMenu();
});

/**
 * Load user info
 */
async function loadUserInfo() {
    try {
        const user = await apiGetCurrentUser();
        if (user) {
            document.getElementById('userName').textContent = user.username;
            document.getElementById('userRole').textContent = (user.roles || []).join(', ') || 'Admin';
        }
    } catch (error) {
        console.error('Error loading user info:', error);
    }
}

/**
 * Load banks for template creation
 */
async function loadBanks() {
    try {
        const result = await apiGetBanks();
        banks = Array.isArray(result) ? result : (result && result.data ? result.data : []);
        populateBankSelect();
    } catch (error) {
        console.error('Error loading banks:', error);
        showToast('Error loading banks. Using defaults.', 'warning');
        banks = [{ id: 1, name: 'BDO' }, { id: 2, name: 'Maya' }, { id: 3, name: 'Security Bank' }];
        populateBankSelect();
    }
}

function populateBankSelect() {
    const select = document.getElementById('bankSelect');
    if (!select) return;

    banks.forEach(bank => {
        const option = document.createElement('option');
        option.value = bank.id;
        option.textContent = bank.name;
        select.appendChild(option);
    });
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

/**
 * Drag and Drop Handlers
 */
function handleDragStart(event, type) {
    dragType = type;
    event.dataTransfer.setData('text/plain', type);
    event.dataTransfer.effectAllowed = 'move';
}

function handleDragOver(event) {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'move';
}

function handleDrop(event) {
    event.preventDefault();
    const type = event.dataTransfer.getData('text/plain') || dragType;

    if (type) {
        addField(type);
    }
}

/**
 * Field Management
 */
function addField(type) {
    const defaultLabel = type.charAt(0).toUpperCase() + type.slice(1) + ' Field';
    const fieldId = `field_${Date.now()}`;

    const newField = {
        id: fieldId,
        type: type,
        label: defaultLabel,
        required: false,
        placeholder: '',
        options: type === 'select' ? ['Option 1', 'Option 2'] : null,
        validation: {},
        show_if: null
    };

    fields.push(newField);
    renderCanvas();
    selectField(fieldId);

    const emptyState = document.getElementById('emptyState');
    if (emptyState) emptyState.style.display = 'none';
}

function deleteField(id) {
    fields = fields.filter(f => f.id !== id);
    if (selectedFieldId === id) selectedFieldId = null;
    renderCanvas();
    renderProperties();

    if (fields.length === 0) {
        const emptyState = document.getElementById('emptyState');
        if (emptyState) emptyState.style.display = 'flex';
    }
}

function selectField(id) {
    selectedFieldId = id;
    renderCanvas();
    renderProperties();
}

/**
 * Rendering
 */
function renderCanvas() {
    const previewArea = document.getElementById('previewArea');
    if (!previewArea) return;

    // Clear current fields but keep empty state
    const existingFields = previewArea.querySelectorAll('.preview-field');
    existingFields.forEach(f => f.remove());

    fields.forEach(field => {
        const div = document.createElement('div');
        div.className = `preview-field ${selectedFieldId === field.id ? 'active' : ''}`;
        div.onclick = (e) => {
            e.stopPropagation();
            selectField(field.id);
        };

        const optionsDisplay = field.type === 'select' && field.options
            ? `<div style="font-size: 12px; color: var(--gray); margin-top: 4px;">Options: ${field.options.join(', ')}</div>`
            : '';
        const showIfDisplay = field.show_if
            ? `<div style="font-size: 12px; color: var(--warning); margin-top: 4px;">⚡ Conditional</div>`
            : '';

        div.innerHTML = `
            <div class="field-header">
                <span class="field-label">${escapeHtml(field.label)} ${field.required ? '<span class="required-mark">*</span>' : ''}</span>
                <div class="field-actions">
                    <button class="btn btn-sm btn-outline" onclick="event.stopPropagation(); deleteField('${field.id}')">Delete</button>
                </div>
            </div>
            <div class="field-type">Type: ${field.type}</div>
            ${optionsDisplay}
            ${showIfDisplay}
        `;

        previewArea.appendChild(div);
    });

    updateJSONPreview();
}

function renderProperties() {
    const panel = document.getElementById('propertiesPanel');
    const field = fields.find(f => f.id === selectedFieldId);

    if (!field) {
        panel.innerHTML = '<div class="empty-state"><p>Select a field to edit</p></div>';
        return;
    }

    let optionsHtml = '';
    if (field.type === 'select') {
        optionsHtml = `
            <div class="config-group">
                <label class="config-label">Options (one per line)</label>
                <textarea class="form-textarea" onchange="updateFieldProperty('options', this.value.split('\\n'))" rows="4">${(field.options || []).join('\n')}</textarea>
            </div>
        `;
    }

    let conditionHtml = '';
    if (field.show_if) {
        conditionHtml = JSON.stringify(field.show_if, null, 2);
    }

    panel.innerHTML = `
        <h4 class="section-title">Field Properties</h4>
        
        <div class="config-group">
            <label class="config-label">Field ID</label>
            <input type="text" class="form-input" value="${field.id}" onchange="updateFieldProperty('id', this.value)">
        </div>
        
        <div class="config-group">
            <label class="config-label">Label</label>
            <input type="text" class="form-input" value="${escapeHtml(field.label)}" onchange="updateFieldProperty('label', this.value)">
        </div>
        
        <div class="config-group">
            <label class="config-label">Required</label>
            <select class="form-select" onchange="updateFieldProperty('required', this.value === 'true')">
                <option value="false" ${!field.required ? 'selected' : ''}>No</option>
                <option value="true" ${field.required ? 'selected' : ''}>Yes</option>
            </select>
        </div>
        
        <div class="config-group">
            <label class="config-label">Placeholder</label>
            <input type="text" class="form-input" value="${escapeHtml(field.placeholder || '')}" 
                   onchange="updateFieldProperty('placeholder', this.value)" placeholder="Enter placeholder text">
        </div>
        
        ${optionsHtml}
        
        <div class="config-group">
            <label class="config-label">Condition (show_if)</label>
            <textarea class="form-textarea" placeholder='{"field": "other_id", "operator": "equals", "value": "xyz"}' 
                      onchange="updateFieldCondition(this.value)" rows="4">${conditionHtml}</textarea>
            <small class="form-help">Use "all" for AND, "any" for OR, "not" for NOT conditions</small>
        </div>
        
        <div class="config-group">
            <label class="config-label">Validation Rules</label>
            <div class="validation-rules">
                <input type="number" class="form-input" placeholder="Min length" 
                       style="width: 48%;" onchange="updateValidation('minLength', this.value)">
                <input type="number" class="form-input" placeholder="Max length" 
                       style="width: 48%;" onchange="updateValidation('maxLength', this.value)">
            </div>
        </div>
    `;
}

/**
 * Property Handlers
 */
function updateFieldProperty(prop, value) {
    const field = fields.find(f => f.id === selectedFieldId);
    if (field) {
        field[prop] = value;
        renderCanvas();
        updateJSONPreview();
    }
}

function updateValidation(rule, value) {
    const field = fields.find(f => f.id === selectedFieldId);
    if (field) {
        if (!field.validation) field.validation = {};
        if (value) {
            field.validation[rule] = parseInt(value);
        } else {
            delete field.validation[rule];
        }
        updateJSONPreview();
    }
}

function updateFieldCondition(value) {
    const field = fields.find(f => f.id === selectedFieldId);
    if (field) {
        try {
            field.show_if = value ? JSON.parse(value) : null;
            renderCanvas();
            updateJSONPreview();
        } catch (e) {
            console.error('Invalid JSON condition');
        }
    }
}

/**
 * JSON Preview and Tabs
 */
function switchTab(tab) {
    const designTab = document.querySelector('.tab:nth-child(1)');
    const jsonTab = document.querySelector('.tab:nth-child(2)');
    const previewArea = document.getElementById('previewArea');
    const jsonPreviewArea = document.getElementById('jsonPreviewArea');

    if (tab === 'design') {
        designTab.classList.add('active');
        jsonTab.classList.remove('active');
        previewArea.style.display = 'flex';
        jsonPreviewArea.style.display = 'none';
    } else {
        designTab.classList.remove('active');
        jsonTab.classList.add('active');
        previewArea.style.display = 'none';
        jsonPreviewArea.style.display = 'block';
        updateJSONPreview();
    }
}

function updateJSONPreview() {
    const code = document.getElementById('jsonPreviewCode');
    if (code) {
        const schema = generateJSONSchema(fields);
        code.textContent = JSON.stringify({
            fields: fields,
            schema: schema
        }, null, 2);
    }
}

/**
 * Generate JSONSchema from fields
 */
function generateJSONSchema(fields) {
    const schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "title": "Form",
        "properties": {},
        "required": []
    };

    fields.forEach(f => {
        const prop = {
            "type": f.type === 'number' ? 'number' : (f.type === 'checkbox' ? 'boolean' : 'string'),
            "title": f.label
        };

        // Add validation rules
        if (f.validation) {
            if (f.validation.minLength) prop.minLength = f.validation.minLength;
            if (f.validation.maxLength) prop.maxLength = f.validation.maxLength;
            if (f.validation.minimum) prop.minimum = f.validation.minimum;
            if (f.validation.maximum) prop.maximum = f.validation.maximum;
            if (f.validation.pattern) prop.pattern = f.validation.pattern;
        }

        if (f.placeholder) prop.description = f.placeholder;

        if (f.type === 'select' && f.options) {
            prop.enum = f.options;
        }

        schema.properties[f.id] = prop;
        if (f.required) schema.required.push(f.id);
    });

    return schema;
}

/**
 * Save Template to Backend
 */
async function saveTemplate() {
    if (fields.length === 0) {
        showToast('Add at least one field before saving', 'error');
        return;
    }

    const bankSelect = document.getElementById('bankSelect');
    const bankId = bankSelect ? parseInt(bankSelect.value) : null;

    if (!bankId) {
        showToast('Please select a bank', 'error');
        return;
    }

    const templateName = document.getElementById('templateName');
    const name = templateName ? templateName.value : prompt('Enter a name for this template:');

    if (!name) {
        showToast('Template name is required', 'error');
        return;
    }

    const version = document.getElementById('templateVersion');
    const templateVersion = version ? version.value : '1.0.0';

    const schema = generateJSONSchema(fields);

    const templateData = {
        bank_id: bankId,
        name: name,
        version: templateVersion,
        schema_json: schema,
        fields: fields,
        description: `Form template created with ${fields.length} fields`,
        active: true
    };

    try {
        showToast(currentTemplate ? 'Updating template...' : 'Saving template...', 'info');

        let url, method, body;

        if (currentTemplate) {
            // Update (PUT)
            method = 'PUT';
            url = `/templates/${currentTemplate.id}`;
            body = {
                name: name,
                schema_json: schema,
                fields: fields,
                description: `Form template created with ${fields.length} fields`,
                active: true
            };
        } else {
            // Create (POST)
            method = 'POST';
            url = '/templates/';
            body = {
                bank_id: bankId,
                name: name,
                version: templateVersion,
                schema_json: schema,
                fields: fields,
                description: `Form template created with ${fields.length} fields`,
                active: true
            };
        }

        const result = await apiRequest(url, {
            method: method,
            body: body
        });

        showToast(currentTemplate ? 'Template updated successfully!' : 'Template saved successfully!', 'success');

        // Reset state
        currentTemplate = null;
        document.getElementById('editingStatus').style.display = 'none';

        fields = [];
        selectedFieldId = null;
        renderCanvas();
        renderProperties();

        if (document.getElementById('emptyState')) {
            document.getElementById('emptyState').style.display = 'flex';
        }

        // Reset form fields
        if (templateName) templateName.value = '';
        if (bankSelect) bankSelect.value = '';
        if (version) version.value = '1.0.0';

        loadTemplates(); // Reload the list

    } catch (error) {
        console.error('Error saving template:', error);
        showToast(error.message || 'Failed to save template. Please try again.', 'error');
    }
}

/**
 * Template Management
 */
async function loadTemplates() {
    try {
        const result = await apiGetTemplates();
        const list = Array.isArray(result) ? result : (result && result.data ? result.data : []);
        renderTemplateList(list);
    } catch (error) {
        console.error('Error loading templates:', error);
    }
}

function renderTemplateList(list) {
    const tbody = document.getElementById('templateTableBody');
    if (!tbody) return;
    tbody.innerHTML = '';

    if (list.length === 0) {
        tbody.innerHTML = '<tr><td colspan="4" style="text-align:center">No templates found</td></tr>';
        return;
    }

    list.forEach(t => {
        const tr = document.createElement('tr');
        const bankName = t.bank ? t.bank.name : (banks.find(b => b.id === t.bank_id)?.name || 'Unknown');
        tr.innerHTML = `
            <td><strong>${escapeHtml(t.name)}</strong></td>
            <td>${escapeHtml(t.version)}</td>
            <td>${escapeHtml(bankName)}</td>
            <td>
                <button class="btn btn-sm btn-primary" onclick="editExistingTemplate(${t.id})">Edit</button>
                <button class="btn btn-sm btn-danger" onclick="deleteExistingTemplate(${t.id})">Delete</button>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

function toggleTemplateList() {
    const section = document.getElementById('templateListSection');
    const icon = document.getElementById('listToggleIcon');
    if (section.style.display === 'none') {
        section.style.display = 'block';
        icon.classList.replace('fa-chevron-down', 'fa-chevron-up');
    } else {
        section.style.display = 'none';
        icon.classList.replace('fa-chevron-up', 'fa-chevron-down');
    }
}

async function editExistingTemplate(id) {
    try {
        const t = await apiRequest(`/templates/${id}`);
        currentTemplate = t; // Track we are editing

        // Populate builder
        fields = Array.isArray(t.fields) ? t.fields : [];
        document.getElementById('templateName').value = t.name || '';
        document.getElementById('templateVersion').value = t.version || '1.0.0';
        document.getElementById('bankSelect').value = t.bank_id;

        // Show status
        document.getElementById('currentTemplateId').textContent = t.id;
        document.getElementById('editingStatus').style.display = 'block';

        renderCanvas();
        renderProperties();

        // Hide list if open
        document.getElementById('templateListSection').style.display = 'none';
        document.getElementById('listToggleIcon').classList.replace('fa-chevron-up', 'fa-chevron-down');

        showToast(`Editing template: ${t.name}`, 'info');

        const emptyState = document.getElementById('emptyState');
        if (emptyState && fields.length > 0) emptyState.style.display = 'none';

        window.scrollTo({ top: 0, behavior: 'smooth' });
    } catch (error) {
        showToast('Error loading template for edit', 'error');
    }
}

function cancelEdit() {
    currentTemplate = null;
    document.getElementById('editingStatus').style.display = 'none';
    fields = [];
    selectedFieldId = null;
    document.getElementById('templateName').value = '';
    document.getElementById('bankSelect').value = '';
    renderCanvas();
    renderProperties();
    if (document.getElementById('emptyState')) document.getElementById('emptyState').style.display = 'flex';
    showToast('Edit cancelled', 'info');
}

async function deleteExistingTemplate(id) {
    if (!confirm('Are you sure you want to delete this template?')) return;
    try {
        await apiRequest(`/templates/${id}`, { method: 'DELETE' });
        showToast('Template deleted', 'success');
        loadTemplates();
    } catch (error) {
        showToast('Error deleting template', 'error');
    }
}

function previewJSON() {
    switchTab('json');
}

/**
 * Helpers
 */
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

