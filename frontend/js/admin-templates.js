/**
 * Admin Template Builder Module
 * Handles dragging fields, editing properties, and saving templates
 */

let fields = [];
let selectedFieldId = null;
let dragType = null;

document.addEventListener('DOMContentLoaded', () => {
    if (typeof requireAuth === 'function') requireAuth();
    loadUserInfo();
    setupMobileMenu();
});

/**
 * Load user info - simplified for development
 */
function loadUserInfo() {
    try {
        if (typeof apiGetCurrentUser === 'function') {
            apiGetCurrentUser().then(user => {
                if (user) {
                    document.getElementById('userName').textContent = user.username;
                    document.getElementById('userRole').textContent = (user.roles || []).join(', ') || 'Admin';
                }
            });
        }
    } catch (error) {
        console.error('Error loading user info:', error);
    }
}

/**
 * Setup mobile menu toggle
 */
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
    const newField = {
        id: `field_${Date.now()}`,
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
    selectField(newField.id);
    document.getElementById('emptyState').style.display = 'none';
}

function deleteField(id) {
    fields = fields.filter(f => f.id !== id);
    if (selectedFieldId === id) selectedFieldId = null;
    renderCanvas();
    renderProperties();

    if (fields.length === 0) {
        document.getElementById('emptyState').style.display = 'flex';
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
    const emptyState = document.getElementById('emptyState');

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

        div.innerHTML = `
            <div style="font-weight: 600; font-size: 14px; margin-bottom: 5px;">
                ${escapeHtml(field.label)} ${field.required ? '<span style="color:red">*</span>' : ''}
            </div>
            <div style="color: var(--gray-500); font-size: 13px;">
                Type: ${field.type} | ID: ${field.id}
            </div>
            <div class="actions">
                <button class="btn btn-sm btn-outline" onclick="deleteField('${field.id}')">Delete</button>
            </div>
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
                <textarea onchange="updateFieldProperty('options', this.value.split('\\n'))" rows="4">${(field.options || []).join('\n')}</textarea>
            </div>
        `;
    }

    panel.innerHTML = `
        <div class="config-group">
            <label class="config-label">Field ID</label>
            <input type="text" value="${field.id}" onchange="updateFieldProperty('id', this.value)">
        </div>
        <div class="config-group">
            <label class="config-label">Label</label>
            <input type="text" value="${escapeHtml(field.label)}" onchange="updateFieldProperty('label', this.value)">
        </div>
        <div class="config-group">
            <label class="config-label">Required</label>
            <select onchange="updateFieldProperty('required', this.value === 'true')">
                <option value="false" ${!field.required ? 'selected' : ''}>No</option>
                <option value="true" ${field.required ? 'selected' : ''}>Yes</option>
            </select>
        </div>
        ${optionsHtml}
        <div class="config-group">
            <label class="config-label">Condition (show_if)</label>
            <textarea placeholder='{"field": "other_id", "operator": "equals", "value": "xyz"}' 
                      onchange="updateFieldCondition(this.value)" rows="4">${field.show_if ? JSON.stringify(field.show_if, null, 2) : ''}</textarea>
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
    }
}

function updateFieldCondition(value) {
    const field = fields.find(f => f.id === selectedFieldId);
    if (field) {
        try {
            field.show_if = value ? JSON.parse(value) : null;
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
        code.textContent = JSON.stringify(fields, null, 2);
    }
}

/**
 * Actions
 */
function saveTemplate() {
    if (fields.length === 0) {
        showToast('Add at least one field before saving', 'warning');
        return;
    }

    const templateName = prompt('Enter a name for this template:');
    if (!templateName) return;

    const templateData = {
        name: templateName,
        fields: fields,
        json_schema: generateJSONSchema(fields)
    };

    showToast('Template layout saved (Simulated)', 'success');
    console.log('Saved Template:', templateData);
}

function generateJSONSchema(fields) {
    const schema = {
        type: "object",
        properties: {},
        required: []
    };

    fields.forEach(f => {
        schema.properties[f.id] = { type: f.type === 'number' ? 'number' : 'string' };
        if (f.required) schema.required.push(f.id);
    });

    return schema;
}

function previewJSON() {
    switchTab('json');
}

/**
 * Helpers
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
