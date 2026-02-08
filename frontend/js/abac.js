// ABAC Management Module - Enhanced with Metadata-Driven Policy Builder
// Handles attribute-based access control functionality with dynamic dropdowns

/**
 * @typedef {Object} OperatorDefinition
 * @property {string} value - Technical operator value
 * @property {string} label - User-friendly label
 * @property {string} [description] - Help text
 */

/**
 * @typedef {Object} ValueOption
 * @property {string} value - Actual value
 * @property {string} label - Display label
 */

/**
 * @typedef {Object} AttributeDefinition
 * @property {string} key - Attribute key (e.g., 'user.department')
 * @property {string} label - User-friendly label
 * @property {string} [description] - Help text
 * @property {string} value_type - Type: 'number', 'string', 'enum', 'boolean'
 * @property {OperatorDefinition[]} operators - Allowed operators
 * @property {string} [value_source] - API endpoint for values
 * @property {ValueOption[]} [static_values] - Static value options
 * @property {string} [input_placeholder] - Placeholder text
 */

// Global state for ABAC metadata
let abacMetadata = null;
let cachedValueOptions = {};

/**
 * Initialize ABAC page
 */
document.addEventListener('DOMContentLoaded', async () => {
    if (typeof requireAuth === 'function') requireAuth();
    loadUserInfo();
    
    // Load ABAC metadata first
    try {
        await loadAbacMetadata();
    } catch (error) {
        console.error('Error loading ABAC metadata:', error);
        showToast('Error loading policy builder configuration', 'error');
    }
    
    loadPolicies();
    setupMobileMenu();
    
    // Enforce UI permissions after a short delay
    if (typeof enforceUIPermissions === 'function') {
        setTimeout(enforceUIPermissions, 100);
    }
});

/**
 * Load ABAC metadata from backend
 */
async function loadAbacMetadata() {
    const data = await apiGetAbacAttributes();
    abacMetadata = data;
    
    // Pre-cache static values for enum attributes
    if (abacMetadata && abacMetadata.attribute_groups) {
        for (const group of abacMetadata.attribute_groups) {
            for (const attr of group.attributes) {
                if (attr.static_values && attr.static_values.length > 0) {
                    cachedValueOptions[attr.key] = attr.static_values;
                }
            }
        }
    }
    
    return abacMetadata;
}

/**
 * Load current user info for sidebar
 */
async function loadUserInfo() {
    try {
        const currentUser = await apiGetCurrentUser();
        if (currentUser) {
            document.getElementById('userName').textContent = currentUser.full_name || currentUser.username;
            document.getElementById('userRole').textContent = currentUser.roles?.join(', ') || 'User';
        }

        // Update permissions in session storage
        let permissions = [];
        try {
            const permData = await apiGetUserPermissions();
            permissions = permData.permissions || [];
        } catch (err) {
            console.warn('Could not fetch permissions during loadUserInfo:', err);
        }

        // Update the session data with fresh permissions
        const session = getCurrentUser();
        if (session) {
            session.permissions = permissions;
            session.is_admin = currentUser.is_superuser || currentUser.user_role === 'admin';
            localStorage.setItem(SESSION_KEY, JSON.stringify(session));
        }
    } catch (error) {
        console.error('Error loading user info:', error);
    }
}

/**
 * Setup mobile menu
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
 * Toggle add policy form visibility
 */
function toggleAddPolicyForm() {
    const form = document.getElementById('addPolicyForm');
    if (form) {
        const isVisible = form.style.display !== 'none';
        if (isVisible) {
            form.style.display = 'none';
            resetPolicyForm();
        } else {
            form.style.display = 'block';
        }
    }
}

/**
 * Cancel policy form and reset
 */
function cancelPolicyForm() {
    resetPolicyForm();
    toggleAddPolicyForm();
}

/**
 * Load and display all ABAC policies
 */
async function loadPolicies() {
    try {
        const policies = await apiGetPolicies();
        const tableBody = document.getElementById('policiesTableBody');
        if (!tableBody) return;

        tableBody.innerHTML = '';

        if (!policies || policies.length === 0) {
            tableBody.innerHTML = '<tr><td colspan="7" style="text-align: center;">No policies found</td></tr>';
            return;
        }

        policies.forEach(policy => {
            const row = createPolicyRow(policy);
            tableBody.appendChild(row);
        });
        
        if (typeof enforceUIPermissions === 'function') {
            enforceUIPermissions();
        }
    } catch (error) {
        console.error('Error loading policies:', error);
        showToast('Error loading policies', 'error');
    }
}

/**
 * Get user-friendly operator label from technical value
 * @param {string} operatorValue - Technical operator (e.g., '==')
 * @returns {string} User-friendly label (e.g., 'is')
 */
function getOperatorLabel(operatorValue) {
    if (!abacMetadata || !abacMetadata.global_operators) {
        // Fallback mapping for non-technical display
        const fallbackMap = {
            '==': 'is',
            '!=': 'is not',
            '>': 'is greater than',
            '<': 'is less than',
            '>=': 'is at least',
            '<=': 'is at most',
            'contains': 'contains',
            'in': 'is one of',
            'not_in': 'is not one of',
            'startswith': 'starts with',
            'endswith': 'ends with'
        };
        return fallbackMap[operatorValue] || operatorValue;
    }
    
    const op = abacMetadata.global_operators.find(o => o.value === operatorValue);
    return op ? op.label : operatorValue;
}

/**
 * Get attribute label from key
 * @param {string} attrKey - Attribute key (e.g., 'user.department')
 * @returns {string} User-friendly label
 */
function getAttributeLabel(attrKey) {
    if (!abacMetadata || !abacMetadata.attribute_groups) {
        return attrKey;
    }
    
    for (const group of abacMetadata.attribute_groups) {
        const attr = group.attributes.find(a => a.key === attrKey);
        if (attr) return attr.label;
    }
    return attrKey;
}

/**
 * Get user-friendly label for an attribute reference
 * @param {string} refKey - The attribute reference key (e.g., "subject.user_id")
 * @returns {string} - Human-readable label
 */
function getAttributeRefLabel(refKey) {
    // Map of common attribute references to user-friendly labels
    const refLabels = {
        'subject.user_id': 'Current User\'s ID',
        'subject.bank_id': 'Current User\'s Bank ID',
        'user.id': 'Current User\'s ID',
        'user.bank_id': 'Current User\'s Bank ID'
    };
    
    return refLabels[refKey] || refKey;
}

/**
 * Create a table row for a policy
 * @param {object} policy 
 * @returns {HTMLElement}
 */
function createPolicyRow(policy) {
    const row = document.createElement('tr');
    
    // Format rules as user-friendly badges
    let rulesDisplay = '<div class="policy-rule-display">';
    if (policy.rules && policy.rules.rules && Array.isArray(policy.rules.rules)) {
        if (policy.rules.rules.length === 0) {
            rulesDisplay += '<span class="badge badge-info">No conditions</span>';
        } else {
            policy.rules.rules.forEach(rule => {
                const fieldLabel = getAttributeLabel(rule.field || '');
                const operatorLabel = getOperatorLabel(rule.operator || '');
                
                // Handle attribute reference values
                let valueDisplay = '';
                if (rule.value && typeof rule.value === 'object' && rule.value.attribute) {
                    // Format attribute reference nicely
                    const refLabel = getAttributeRefLabel(rule.value.attribute);
                    valueDisplay = `<em>${escapeHtml(refLabel)}</em>`;
                } else {
                    valueDisplay = escapeHtml(String(rule.value || ''));
                }
                
                rulesDisplay += `
                    <div class="rule-badge">
                        <span class="rule-field">${escapeHtml(fieldLabel)}</span>
                        <span class="rule-operator">${escapeHtml(operatorLabel)}</span>
                        <span class="rule-value">${valueDisplay}</span>
                    </div>
                `;
            });
        }
    } else {
        rulesDisplay += '<span class="badge badge-info">No conditions</span>';
    }
    rulesDisplay += '</div>';
    
    const statusBadge = policy.is_active 
        ? '<span class="badge badge-success">Active</span>' 
        : '<span class="badge badge-secondary">Inactive</span>';
    
    const createdAt = policy.created_at 
        ? new Date(policy.created_at).toLocaleString('en-US', {
            month: 'short', day: 'numeric', year: 'numeric', 
            hour: '2-digit', minute: '2-digit'
        }) 
        : 'N/A';
    const updatedAt = policy.updated_at 
        ? new Date(policy.updated_at).toLocaleString('en-US', {
            month: 'short', day: 'numeric', year: 'numeric', 
            hour: '2-digit', minute: '2-digit'
        }) 
        : 'N/A';

    row.innerHTML = `
        <td>${escapeHtml(policy.name)}</td>
        <td>${escapeHtml(policy.description || 'N/A')}</td>
        <td>${rulesDisplay}</td>
        <td>${statusBadge}</td>
        <td style="font-size: 0.85em;">${createdAt}</td>
        <td style="font-size: 0.85em;">${updatedAt}</td>
        <td>
            <button class="btn btn-sm btn-primary" onclick="editPolicy(${policy.id})" data-permission="policies" data-action="update">Edit</button>
            <button class="btn btn-sm btn-danger" onclick="deletePolicy(${policy.id})" data-permission="policies" data-action="delete">Delete</button>
        </td>
    `;

    return row;
}

/**
 * Handle policy creation and update
 */
const addPolicyForm = document.getElementById('addPolicyForm');
if (addPolicyForm) {
    addPolicyForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const policyName = document.getElementById('policyName').value;
        const policyDescription = document.getElementById('policyDescription').value;
        const isActive = document.getElementById('isActive')?.checked ?? true;

        const rules = buildPolicyRules();
        
        if (!rules.rules || rules.rules.length === 0) {
            showToast('Please add at least one condition', 'error');
            return;
        }

        const policyData = {
            name: policyName,
            description: policyDescription,
            rules: rules,
            is_active: isActive
        };

        try {
            const editId = addPolicyForm.dataset.editId;
            
            if (editId) {
                await apiUpdatePolicy(parseInt(editId), policyData);
                showToast('Policy updated successfully', 'success');
            } else {
                await apiCreatePolicy(policyData);
                showToast('Policy created successfully', 'success');
            }

            resetPolicyForm();
            toggleAddPolicyForm();
            loadPolicies();
        } catch (error) {
            console.error('Error saving policy:', error);
            showToast(error.message || 'Error saving policy', 'error');
        }
    });
}

/**
 * Reset policy form to initial state
 */
function resetPolicyForm() {
    const form = document.getElementById('addPolicyForm');
    if (!form) return;
    
    form.reset();
    delete form.dataset.editId;
    
    const conditionsBuilder = document.getElementById('conditionsBuilder');
    conditionsBuilder.innerHTML = `
        <div class="empty-state" id="emptyRulesState">
            <p>No conditions added yet. Click "Add Condition" to start building your policy.</p>
        </div>
    `;
    
    const submitBtn = form.querySelector('button[type="submit"]');
    if (submitBtn) submitBtn.textContent = 'Create Policy';
    
    const formTitle = document.getElementById('formTitle');
    if (formTitle) formTitle.textContent = 'Add New Policy';
}

/**
 * Build attribute dropdown options from metadata
 * @returns {string} HTML options string
 */
function buildAttributeOptions() {
    let options = '<option value="">Select Attribute</option>';
    
    if (!abacMetadata || !abacMetadata.attribute_groups) {
        // Fallback if metadata not loaded
        options += `
            <optgroup label="User Attributes">
                <option value="user.id">User ID</option>
                <option value="user.user_role">User Role</option>
                <option value="user.department">Department</option>
                <option value="user.location">Location</option>
                <option value="user.level">User Level</option>
            </optgroup>
            <optgroup label="Resource Attributes">
                <option value="resource.type">Resource Type</option>
                <option value="resource.status">Resource Status</option>
            </optgroup>
        `;
        return options;
    }
    
    for (const group of abacMetadata.attribute_groups) {
        options += `<optgroup label="${escapeHtml(group.name)}">`;
        for (const attr of group.attributes) {
            const description = attr.description ? ` title="${escapeHtml(attr.description)}"` : '';
            options += `<option value="${escapeHtml(attr.key)}"${description}>${escapeHtml(attr.label)}</option>`;
        }
        options += '</optgroup>';
    }
    
    return options;
}

/**
 * Get attribute definition by key
 * @param {string} attrKey 
 * @returns {AttributeDefinition|null}
 */
function getAttributeDefinition(attrKey) {
    if (!abacMetadata || !abacMetadata.attribute_groups) return null;
    
    for (const group of abacMetadata.attribute_groups) {
        const attr = group.attributes.find(a => a.key === attrKey);
        if (attr) return attr;
    }
    return null;
}

/**
 * Build operator dropdown options for a specific attribute
 * @param {string} attrKey - Attribute key
 * @returns {string} HTML options string
 */
function buildOperatorOptions(attrKey) {
    const attr = getAttributeDefinition(attrKey);
    
    if (!attr || !attr.operators || attr.operators.length === 0) {
        // Fallback operators with user-friendly labels
        return `
            <option value="==">is</option>
            <option value="!=">is not</option>
        `;
    }
    
    let options = '';
    for (const op of attr.operators) {
        const description = op.description ? ` title="${escapeHtml(op.description)}"` : '';
        options += `<option value="${escapeHtml(op.value)}"${description}>${escapeHtml(op.label)}</option>`;
    }
    
    return options;
}

/**
 * Build value input HTML based on attribute type
 * @param {string} attrKey - Attribute key
 * @param {string|Object} [currentValue] - Current value for editing
 * @returns {string} HTML string for value input
 */
function buildValueInput(attrKey, currentValue = '') {
    const attr = getAttributeDefinition(attrKey);
    
    // Check if current value is an attribute reference
    let isAttributeRef = false;
    let refValue = '';
    let staticValue = '';
    
    if (typeof currentValue === 'object' && currentValue !== null && currentValue.attribute) {
        isAttributeRef = true;
        refValue = currentValue.attribute;
    } else {
        staticValue = String(currentValue);
    }
    
    const escapedValue = escapeHtml(staticValue);
    
    if (!attr) {
        return `<input type="text" class="condition-value" placeholder="Enter value" value="${escapedValue}">`;
    }
    
    // Check if this attribute allows referencing other attributes
    if (attr.allow_attribute_reference && attr.reference_attributes && attr.reference_attributes.length > 0) {
        // Build a compound input with toggle between static value and attribute reference
        let refOptions = '<option value="">Select attribute</option>';
        for (const ref of attr.reference_attributes) {
            const selected = ref.value === refValue ? ' selected' : '';
            refOptions += `<option value="${escapeHtml(ref.value)}"${selected}>${escapeHtml(ref.label)}</option>`;
        }
        
        return `
            <div class="value-input-wrapper">
                <div class="value-type-toggle">
                    <label>
                        <input type="radio" name="value-type-${escapeHtml(attrKey)}" value="static" ${!isAttributeRef ? 'checked' : ''} onchange="toggleValueType(this)">
                        Static Value
                    </label>
                    <label>
                        <input type="radio" name="value-type-${escapeHtml(attrKey)}" value="reference" ${isAttributeRef ? 'checked' : ''} onchange="toggleValueType(this)">
                        Compare to Attribute
                    </label>
                </div>
                <div class="value-static-input" ${isAttributeRef ? 'style="display:none"' : ''}>
                    ${buildStaticValueInput(attr, staticValue)}
                </div>
                <div class="value-reference-input" ${!isAttributeRef ? 'style="display:none"' : ''}>
                    <select class="condition-value-ref">
                        ${refOptions}
                    </select>
                </div>
            </div>
        `;
    }
    
    return buildStaticValueInput(attr, staticValue);
}

/**
 * Build static value input based on attribute type
 */
function buildStaticValueInput(attr, currentValue = '') {
    const escapedValue = escapeHtml(String(currentValue));
    
    switch (attr.value_type) {
        case 'number':
            return `
                <input type="number" class="condition-value" 
                    placeholder="${escapeHtml(attr.input_placeholder || 'Enter number')}" 
                    value="${escapedValue}">
            `;
            
        case 'boolean':
            const boolVals = attr.static_values || [
                { value: 'true', label: 'Yes' },
                { value: 'false', label: 'No' }
            ];
            let boolOptions = '';
            for (const opt of boolVals) {
                const selected = opt.value === currentValue ? ' selected' : '';
                boolOptions += `<option value="${escapeHtml(opt.value)}"${selected}>${escapeHtml(opt.label)}</option>`;
            }
            return `<select class="condition-value">${boolOptions}</select>`;
            
        case 'enum':
            // Use cached or static values
            const values = cachedValueOptions[attr.key] || attr.static_values || [];
            
            if (values.length === 0 && attr.value_source) {
                // No values available - show loading indicator and fetch
                fetchAttributeValues(attr.key);
                return `
                    <select class="condition-value" data-attr-key="${escapeHtml(attr.key)}">
                        <option value="">Loading options...</option>
                    </select>
                `;
            }
            
            let enumOptions = '<option value="">Select value</option>';
            for (const opt of values) {
                const selected = opt.value === currentValue ? ' selected' : '';
                enumOptions += `<option value="${escapeHtml(opt.value)}"${selected}>${escapeHtml(opt.label)}</option>`;
            }
            return `<select class="condition-value">${enumOptions}</select>`;
            
        case 'string':
        default:
            return `
                <input type="text" class="condition-value" 
                    placeholder="${escapeHtml(attr.input_placeholder || 'Enter value')}" 
                    value="${escapedValue}">
            `;
    }
}

/**
 * Toggle between static value and attribute reference inputs
 */
function toggleValueType(radio) {
    const wrapper = radio.closest('.value-input-wrapper');
    const staticInput = wrapper.querySelector('.value-static-input');
    const refInput = wrapper.querySelector('.value-reference-input');
    
    if (radio.value === 'static') {
        staticInput.style.display = '';
        refInput.style.display = 'none';
    } else {
        staticInput.style.display = 'none';
        refInput.style.display = '';
    }
}

/**
 * Fetch attribute values from backend API
 * @param {string} attrKey 
 */
async function fetchAttributeValues(attrKey) {
    const attr = getAttributeDefinition(attrKey);
    if (!attr || !attr.value_source) return;
    
    try {
        let values = [];
        
        // Map common endpoints to API functions
        if (attr.value_source.includes('/roles')) {
            const roles = await apiGetRoles();
            values = (Array.isArray(roles) ? roles : []).map(r => ({
                value: r.name,
                label: r.name.charAt(0).toUpperCase() + r.name.slice(1)
            }));
        } else if (attr.value_source.includes('/departments')) {
            const departments = await apiGetDepartments();
            values = (Array.isArray(departments) ? departments : []).map(d => ({
                value: d.name,
                label: d.name
            }));
        } else if (attr.value_source.includes('/locations')) {
            const locations = await apiGetLocations();
            values = (Array.isArray(locations) ? locations : []).map(l => ({
                value: l.name,
                label: l.name
            }));
        } else if (attr.value_source.includes('/banks')) {
            const banks = await apiGetBanks();
            values = (Array.isArray(banks) ? banks : []).map(b => ({
                value: String(b.id),
                label: b.name || `Bank ${b.id}`
            }));
        }
        
        // Cache the values
        cachedValueOptions[attrKey] = values;
        
        // Update all dropdowns for this attribute
        const selects = document.querySelectorAll(`select.condition-value[data-attr-key="${attrKey}"]`);
        selects.forEach(select => {
            const currentVal = select.value;
            let optionsHtml = '<option value="">Select value</option>';
            for (const opt of values) {
                const selected = opt.value === currentVal ? ' selected' : '';
                optionsHtml += `<option value="${escapeHtml(opt.value)}"${selected}>${escapeHtml(opt.label)}</option>`;
            }
            select.innerHTML = optionsHtml;
            select.removeAttribute('data-attr-key');
        });
        
    } catch (error) {
        console.error(`Error fetching values for ${attrKey}:`, error);
    }
}

/**
 * Handle attribute selection change - update operators and value input
 * @param {HTMLSelectElement} selectElement 
 */
function onAttributeChange(selectElement) {
    const conditionItem = selectElement.closest('.condition-item');
    if (!conditionItem) return;
    
    const attrKey = selectElement.value;
    const operatorSelect = conditionItem.querySelector('.condition-operator');
    const valueContainer = conditionItem.querySelector('.value-container');
    
    // Update operators with user-friendly labels
    if (operatorSelect) {
        operatorSelect.innerHTML = buildOperatorOptions(attrKey);
    }
    
    // Update value input based on attribute type
    if (valueContainer) {
        valueContainer.innerHTML = buildValueInput(attrKey);
    }
}

/**
 * Add a condition to the policy builder
 */
function addCondition() {
    const conditionsBuilder = document.getElementById('conditionsBuilder');
    
    // Hide empty state
    const emptyState = document.getElementById('emptyRulesState');
    if (emptyState) {
        emptyState.style.display = 'none';
    }

    const conditionDiv = document.createElement('div');
    conditionDiv.className = 'condition-item';
    
    const attributeOptions = buildAttributeOptions();

    conditionDiv.innerHTML = `
        <div class="form-group">
            <label>Attribute</label>
            <select class="condition-attribute" onchange="onAttributeChange(this)">
                ${attributeOptions}
            </select>
        </div>
        <div class="form-group">
            <label>Operator</label>
            <select class="condition-operator">
                <option value="==">is</option>
                <option value="!=">is not</option>
            </select>
        </div>
        <div class="form-group">
            <label>Value</label>
            <div class="value-container">
                <input type="text" class="condition-value" placeholder="Select an attribute first">
            </div>
        </div>
        <button type="button" class="btn-remove" onclick="removeCondition(this)" title="Remove condition">×</button>
    `;

    conditionsBuilder.appendChild(conditionDiv);
}

/**
 * Remove a condition
 */
function removeCondition(button) {
    button.parentElement.remove();
    
    const conditionsBuilder = document.getElementById('conditionsBuilder');
    const conditions = conditionsBuilder.querySelectorAll('.condition-item');
    const emptyState = document.getElementById('emptyRulesState');
    
    if (conditions.length === 0 && emptyState) {
        emptyState.style.display = 'block';
    }
}

/**
 * Build policy rules from conditions
 */
function buildPolicyRules() {
    const conditions = document.querySelectorAll('.condition-item');
    const rules = [];

    conditions.forEach(condition => {
        const field = condition.querySelector('.condition-attribute').value;
        const operator = condition.querySelector('.condition-operator').value;
        
        // Check if this condition uses attribute reference
        const wrapper = condition.querySelector('.value-input-wrapper');
        let value = '';
        let isAttributeRef = false;
        
        if (wrapper) {
            // Check which radio is selected
            const refRadio = wrapper.querySelector('input[type="radio"][value="reference"]');
            if (refRadio && refRadio.checked) {
                isAttributeRef = true;
                const refSelect = wrapper.querySelector('.condition-value-ref');
                value = refSelect ? refSelect.value : '';
            } else {
                const valueInput = wrapper.querySelector('.condition-value');
                value = valueInput ? valueInput.value : '';
            }
        } else {
            const valueInput = condition.querySelector('.condition-value');
            value = valueInput ? valueInput.value : '';
        }

        if (field && operator && value !== '') {
            let parsedValue;
            
            if (isAttributeRef) {
                // Store as attribute reference object
                parsedValue = { attribute: value };
            } else {
                // Parse value to correct type based on attribute definition
                parsedValue = value;
                const attr = getAttributeDefinition(field);
                
                if (attr) {
                    switch (attr.value_type) {
                        case 'number':
                            parsedValue = Number(value);
                            break;
                        case 'boolean':
                            parsedValue = value === 'true';
                            break;
                        default:
                            parsedValue = value;
                    }
                } else {
                    // Fallback parsing
                    if (!isNaN(value) && value !== '') {
                        parsedValue = Number(value);
                    } else if (value.toLowerCase() === 'true') {
                        parsedValue = true;
                    } else if (value.toLowerCase() === 'false') {
                        parsedValue = false;
                    }
                }
            }

            rules.push({
                field: field,
                operator: operator,
                value: parsedValue
            });
        }
    });

    return {
        condition: 'all',
        rules: rules
    };
}

/**
 * Edit a policy
 */
async function editPolicy(policyId) {
    try {
        const policies = await apiGetPolicies();
        const policy = policies.find(p => p.id === policyId);
        
        if (!policy) {
            showToast('Policy not found', 'error');
            return;
        }

        // Populate form fields
        document.getElementById('policyName').value = policy.name;
        document.getElementById('policyDescription').value = policy.description || '';
        document.getElementById('isActive').checked = policy.is_active;

        // Clear and populate conditions
        const conditionsBuilder = document.getElementById('conditionsBuilder');
        conditionsBuilder.innerHTML = `
            <div class="empty-state" id="emptyRulesState" style="display: none;">
                <p>No conditions added yet. Click "Add Condition" to start building your policy.</p>
            </div>
        `;

        if (policy.rules && policy.rules.rules && Array.isArray(policy.rules.rules) && policy.rules.rules.length > 0) {
            for (const rule of policy.rules.rules) {
                // Add condition element
                addCondition();
                const lastCondition = conditionsBuilder.querySelector('.condition-item:last-child');
                
                // Set attribute
                const attrSelect = lastCondition.querySelector('.condition-attribute');
                attrSelect.value = rule.field || '';
                
                // Trigger attribute change to update operators and value input
                onAttributeChange(attrSelect);
                
                // Set operator
                const opSelect = lastCondition.querySelector('.condition-operator');
                opSelect.value = rule.operator || '==';
                
                // Set value (need slight delay for dynamic inputs to render)
                setTimeout(() => {
                    const wrapper = lastCondition.querySelector('.value-input-wrapper');
                    
                    // Check if value is an attribute reference
                    if (rule.value && typeof rule.value === 'object' && rule.value.attribute) {
                        // This is an attribute reference
                        if (wrapper) {
                            const refRadio = wrapper.querySelector('input[type="radio"][value="reference"]');
                            if (refRadio) {
                                refRadio.checked = true;
                                // Trigger the toggle to show reference dropdown
                                toggleValueType(refRadio, lastCondition);
                                
                                // Set the reference value
                                const refSelect = wrapper.querySelector('.condition-value-ref');
                                if (refSelect) {
                                    refSelect.value = rule.value.attribute;
                                }
                            }
                        }
                    } else {
                        // This is a static value
                        if (wrapper) {
                            const staticRadio = wrapper.querySelector('input[type="radio"][value="static"]');
                            if (staticRadio) {
                                staticRadio.checked = true;
                                toggleValueType(staticRadio, lastCondition);
                            }
                        }
                        const valueInput = lastCondition.querySelector('.condition-value');
                        if (valueInput) {
                            valueInput.value = rule.value !== undefined ? String(rule.value) : '';
                        }
                    }
                }, 100);
            }
        } else {
            document.getElementById('emptyRulesState').style.display = 'block';
        }

        // Show form if hidden
        const form = document.getElementById('addPolicyForm');
        if (form.style.display === 'none') {
            form.style.display = 'block';
        }
        
        // Change form to edit mode
        form.dataset.editId = policyId;
        
        const submitBtn = form.querySelector('button[type="submit"]');
        if (submitBtn) submitBtn.textContent = 'Update Policy';
        
        const formTitle = document.getElementById('formTitle');
        if (formTitle) formTitle.textContent = 'Edit Policy';

    } catch (error) {
        console.error('Error loading policy for edit:', error);
        showToast('Error loading policy', 'error');
    }
}

/**
 * Delete a policy
 */
async function deletePolicy(policyId) {
    if (!confirm('Are you sure you want to delete this policy?')) return;

    try {
        await apiDeletePolicy(policyId);
        showToast('Policy deleted successfully', 'success');
        loadPolicies();
    } catch (error) {
        console.error('Error deleting policy:', error);
        showToast(error.message || 'Error deleting policy', 'error');
    }
}

/**
 * Refresh metadata and cached values
 * Call this when roles/departments/locations are updated
 */
async function refreshAbacMetadata() {
    cachedValueOptions = {};
    await loadAbacMetadata();
    showToast('Policy builder refreshed', 'success');
}

// ============ ABAC Audit Trail Functions ============

let abacAuditCurrentPage = 1;
const abacAuditPageSize = 20;

/**
 * Show the ABAC audit trail modal
 */
function showAbacAuditTrail() {
    const modal = document.getElementById('auditTrailModal');
    if (modal) {
        modal.style.display = 'flex';
        abacAuditCurrentPage = 1;
        loadAbacAuditTrail();
    }
}

/**
 * Close the audit trail modal
 */
function closeAuditTrailModal() {
    const modal = document.getElementById('auditTrailModal');
    if (modal) {
        modal.style.display = 'none';
    }
}

/**
 * Clear audit filters
 */
function clearAuditFilters() {
    document.getElementById('auditActionFilter').value = '';
    document.getElementById('auditDateFrom').value = '';
    document.getElementById('auditDateTo').value = '';
    abacAuditCurrentPage = 1;
    loadAbacAuditTrail();
}

/**
 * Load ABAC audit trail data
 */
async function loadAbacAuditTrail(page = abacAuditCurrentPage) {
    const tableBody = document.getElementById('auditTableBody');
    const pagination = document.getElementById('auditPagination');
    
    if (!tableBody) return;
    
    // Clear the changes store when loading new data
    window.__abacAuditChangesStore = [];
    
    // Show loading state
    tableBody.innerHTML = '<tr><td colspan="5" style="text-align: center; padding: 24px;">Loading audit logs...</td></tr>';
    
    // Get filter values
    const actionType = document.getElementById('auditActionFilter')?.value || '';
    const dateFrom = document.getElementById('auditDateFrom')?.value || '';
    const dateTo = document.getElementById('auditDateTo')?.value || '';
    
    try {
        // Build query params
        let url = `/abac/audit-trail?page=${page}&page_size=${abacAuditPageSize}`;
        if (actionType) url += `&action_type=${encodeURIComponent(actionType)}`;
        if (dateFrom) url += `&start_date=${encodeURIComponent(dateFrom + 'T00:00:00')}`;
        if (dateTo) url += `&end_date=${encodeURIComponent(dateTo + 'T23:59:59')}`;
        
        const response = await apiRequest(url);
        const data = response;
        
        if (!data || !data.items || data.items.length === 0) {
            tableBody.innerHTML = '<tr><td colspan="5" style="text-align: center; padding: 24px; color: #666;">No audit logs found</td></tr>';
            pagination.innerHTML = '';
            return;
        }
        
        // Render audit logs
        tableBody.innerHTML = data.items.map(log => renderAbacAuditLogRow(log)).join('');
        
        // Render pagination
        renderAbacAuditPagination(data.page, data.total_pages, data.total);
        abacAuditCurrentPage = page;
        
    } catch (error) {
        console.error('Error loading audit trail:', error);
        tableBody.innerHTML = '<tr><td colspan="5" style="text-align: center; padding: 24px; color: #dc3545;">Error loading audit logs: ' + escapeHtml(error.message || 'Unknown error') + '</td></tr>';
    }
}

// Store for ABAC audit changes (to pass data to modal)
window.__abacAuditChangesStore = window.__abacAuditChangesStore || [];

/**
 * Render a single audit log row
 */
function renderAbacAuditLogRow(log) {
    // Use common formatDateTime from utils.js for consistent date format
    const timestamp = log.timestamp 
        ? formatDateTime(log.timestamp)
        : (log.created_at ? formatDateTime(log.created_at) : 'N/A');
    
    // Format action badge
    let actionBadge = '';
    const action = (log.action || '').toLowerCase();
    if (action.includes('created')) {
        actionBadge = '<span class="badge badge-success">Created</span>';
    } else if (action.includes('updated')) {
        actionBadge = '<span class="badge badge-warning">Updated</span>';
    } else if (action.includes('deleted')) {
        actionBadge = '<span class="badge badge-danger">Deleted</span>';
    } else {
        actionBadge = `<span class="badge badge-secondary">${escapeHtml(log.action)}</span>`;
    }
    
    // Format resource info
    const resourceType = log.resource_type || 'unknown';
    const resourceId = log.resource_id || 'N/A';
    let resourceName = '';
    if (log.details && log.details.policy_name) {
        resourceName = log.details.policy_name;
    } else if (log.details && log.details.attribute_key) {
        resourceName = log.details.attribute_key;
    }
    
    const resourceInfo = resourceName 
        ? `<strong>${escapeHtml(resourceName)}</strong><br><small style="color: #666;">${resourceType} #${resourceId}</small>`
        : `${resourceType} #${resourceId}`;
    
    // Format performed by info
    const performedBy = log.performed_by || {};
    const username = performedBy.username || log.username || 'Unknown';
    const role = log.details?.performed_by?.role || '';
    const userInfo = role 
        ? `<strong>${escapeHtml(username)}</strong><br><small style="color: #666;">${escapeHtml(role)}</small>`
        : escapeHtml(username);
    
    // Format changes - add View Changes button
    let changesHtml = '-';
    if (log.changes && (log.changes.before || log.changes.after)) {
        const idx = window.__abacAuditChangesStore.push(log.changes) - 1;
        changesHtml = `<button class="btn btn-sm btn-info" onclick="showAbacChangesDetail(${idx})">View Changes</button>`;
    }
    
    return `
        <tr>
            <td style="font-size: 0.85em;">${timestamp}</td>
            <td>${actionBadge}</td>
            <td>${resourceInfo}</td>
            <td>${userInfo}</td>
            <td style="font-size: 0.85em;">${changesHtml}</td>
        </tr>
    `;
}

/**
 * Show ABAC change details from the index
 * @param {number} index - Index in the changes store
 */
function showAbacChangesDetail(index) {
    if (!window.__abacAuditChangesStore || !window.__abacAuditChangesStore[index]) {
        console.error('No changes data found for index', index);
        if (typeof showToast === 'function') {
            showToast('No change details available for this entry', 'error');
        }
        return;
    }
    showAbacChangesModal(window.__abacAuditChangesStore[index]);
}

/**
 * Show detailed ABAC changes in a modal
 * @param {object} changes - Changes object with before/after
 */
function showAbacChangesModal(changes) {
    const before = changes.before || {};
    const after = changes.after || {};
    
    // Get all keys from both before and after, sorted
    const allKeys = Array.from(new Set([
        ...Object.keys(before),
        ...Object.keys(after)
    ])).sort();

    // Format a single value for display
    const formatValue = (value) => {
        if (value === null || value === undefined || value === '') {
            return '<span class="text-muted">—</span>';
        }
        if (typeof value === 'object') {
            return `<pre class="json-block">${escapeHtml(JSON.stringify(value, null, 2))}</pre>`;
        }
        return escapeHtml(String(value));
    };

    let content = '<div class="changes-detail">';
    
    // Show action type if available
    if (changes.action) {
        let actionBadgeClass = 'badge-secondary';
        if (changes.action === 'created') actionBadgeClass = 'badge-success';
        else if (changes.action === 'updated') actionBadgeClass = 'badge-warning';
        else if (changes.action === 'deleted') actionBadgeClass = 'badge-danger';
        
        content += `<div class="changes-meta"><span class="badge ${actionBadgeClass}">${escapeHtml(changes.action)}</span></div>`;
    }

    if (allKeys.length === 0) {
        content += '<p class="text-muted">No field-level changes recorded.</p>';
    } else {
        content += `
            <div class="changes-grid">
                <div class="changes-header">Field</div>
                <div class="changes-header">Before</div>
                <div class="changes-header">After</div>
        `;

        allKeys.forEach((key) => {
            const beforeVal = before[key];
            const afterVal = after[key];
            const changed = JSON.stringify(beforeVal) !== JSON.stringify(afterVal);
            content += `
                <div class="change-key ${changed ? 'change-key--changed' : ''}">${escapeHtml(key)}</div>
                <div class="change-before ${changed ? 'change-cell--changed' : ''}">${formatValue(beforeVal)}</div>
                <div class="change-after ${changed ? 'change-cell--changed' : ''}">${formatValue(afterVal)}</div>
            `;
        });

        content += '</div>';
    }

    content += '</div>';
    
    // Create and show modal
    showAbacChangesDetailModal('Change Details', content);
}

/**
 * Create and show the changes detail modal
 * @param {string} title - Modal title
 * @param {string} content - Modal body content
 */
function showAbacChangesDetailModal(title, content) {
    // Remove existing modal if any
    const existingModal = document.getElementById('abacChangesDetailModal');
    if (existingModal) {
        existingModal.remove();
    }
    
    const modalHtml = `
        <div id="abacChangesDetailModal" class="modal-overlay" style="
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0,0,0,0.6);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 10001;
        ">
            <div class="modal-content" style="
                background: white;
                border-radius: 8px;
                width: 90%;
                max-width: 800px;
                max-height: 90vh;
                overflow: hidden;
                display: flex;
                flex-direction: column;
                box-shadow: 0 4px 20px rgba(0,0,0,0.3);
            ">
                <div class="modal-header" style="
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    padding: 16px 20px;
                    border-bottom: 1px solid #e0e0e0;
                    background: #f8f9fa;
                ">
                    <h3 style="margin: 0; font-size: 1.25rem;">${escapeHtml(title)}</h3>
                    <button onclick="closeAbacChangesDetailModal()" style="
                        background: none;
                        border: none;
                        font-size: 24px;
                        cursor: pointer;
                        color: #666;
                        padding: 0 8px;
                    ">&times;</button>
                </div>
                <div class="modal-body" style="
                    padding: 20px;
                    overflow-y: auto;
                    flex: 1;
                ">
                    ${content}
                </div>
                <div class="modal-footer" style="
                    padding: 12px 20px;
                    border-top: 1px solid #e0e0e0;
                    text-align: right;
                    background: #f8f9fa;
                ">
                    <button onclick="closeAbacChangesDetailModal()" class="btn btn-secondary">Close</button>
                </div>
            </div>
        </div>
    `;
    
    // Add modal styles if not already present
    if (!document.getElementById('abacChangesModalStyles')) {
        const styles = document.createElement('style');
        styles.id = 'abacChangesModalStyles';
        styles.textContent = `
            .changes-detail {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            }
            .changes-meta {
                margin-bottom: 16px;
            }
            .changes-grid {
                display: grid;
                grid-template-columns: 150px 1fr 1fr;
                gap: 1px;
                background: #e0e0e0;
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                overflow: hidden;
            }
            .changes-header {
                background: #f0f0f0;
                font-weight: 600;
                padding: 10px 12px;
                font-size: 0.85em;
            }
            .change-key {
                background: #fafafa;
                padding: 8px 12px;
                font-weight: 500;
                font-size: 0.9em;
                word-break: break-word;
            }
            .change-key--changed {
                background: #fff3cd;
                font-weight: 600;
            }
            .change-before,
            .change-after {
                background: white;
                padding: 8px 12px;
                word-break: break-word;
                font-size: 0.9em;
            }
            .change-cell--changed {
                background: #fffbdd;
            }
            .text-muted {
                color: #999;
                font-style: italic;
            }
            .json-block {
                background: #f8f9fa;
                border: 1px solid #e9ecef;
                border-radius: 4px;
                padding: 8px;
                font-size: 0.8em;
                overflow-x: auto;
                margin: 0;
                white-space: pre-wrap;
                word-wrap: break-word;
                max-height: 200px;
                overflow-y: auto;
            }
        `;
        document.head.appendChild(styles);
    }
    
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    
    // Add click outside to close
    const modal = document.getElementById('abacChangesDetailModal');
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            closeAbacChangesDetailModal();
        }
    });
}

/**
 * Close the changes detail modal
 */
function closeAbacChangesDetailModal() {
    const modal = document.getElementById('abacChangesDetailModal');
    if (modal) {
        modal.remove();
    }
}

/**
 * Format changes between before and after states
 */
function formatAbacChanges(before, after) {
    const changes = [];
    
    // Check for name change
    if (before.name !== after.name) {
        changes.push(`Name: "${escapeHtml(before.name)}" → "${escapeHtml(after.name)}"`);
    }
    
    // Check for description change
    if (before.description !== after.description) {
        changes.push(`Description changed`);
    }
    
    // Check for active status change
    if (before.is_active !== after.is_active) {
        changes.push(`Status: ${before.is_active ? 'Active' : 'Inactive'} → ${after.is_active ? 'Active' : 'Inactive'}`);
    }
    
    // Check for rules change
    if (JSON.stringify(before.rules) !== JSON.stringify(after.rules)) {
        const beforeCount = before.rules?.rules?.length || 0;
        const afterCount = after.rules?.rules?.length || 0;
        changes.push(`Conditions: ${beforeCount} → ${afterCount}`);
    }
    
    return changes.length > 0 
        ? changes.map(c => `<div>${c}</div>`).join('')
        : '<small style="color: #666;">Minor changes</small>';
}

/**
 * Render audit pagination
 */
function renderAbacAuditPagination(currentPage, totalPages, totalItems) {
    const pagination = document.getElementById('auditPagination');
    if (!pagination) return;
    
    if (totalPages <= 1) {
        pagination.innerHTML = `<small style="color: #666;">${totalItems} record(s)</small>`;
        return;
    }
    
    let html = '';
    
    // Previous button
    html += `<button class="btn btn-sm ${currentPage === 1 ? 'btn-secondary disabled' : 'btn-secondary'}" 
        onclick="loadAbacAuditTrail(${currentPage - 1})" ${currentPage === 1 ? 'disabled' : ''}>Previous</button>`;
    
    // Page info
    html += `<span style="padding: 0 12px; line-height: 32px;">Page ${currentPage} of ${totalPages} (${totalItems} total)</span>`;
    
    // Next button
    html += `<button class="btn btn-sm ${currentPage === totalPages ? 'btn-secondary disabled' : 'btn-secondary'}" 
        onclick="loadAbacAuditTrail(${currentPage + 1})" ${currentPage === totalPages ? 'disabled' : ''}>Next</button>`;
    
    pagination.innerHTML = html;
}

// ============ Batch Operations with Celery/Redis ============

/**
 * Export ABAC audit logs using Celery batch processing
 */
async function exportAbacAuditLogs() {
    // Get current filter values
    const actionType = document.getElementById('auditActionFilter')?.value || null;
    const dateFrom = document.getElementById('auditDateFrom')?.value || null;
    const dateTo = document.getElementById('auditDateTo')?.value || null;
    
    // Show export format dialog
    const format = await showExportFormatDialog();
    if (!format) return; // User cancelled
    
    try {
        showToast('Submitting export task...', 'info');
        
        const exportRequest = {
            export_format: format
        };
        
        if (actionType) exportRequest.action_type = actionType;
        if (dateFrom) exportRequest.from_date = dateFrom + 'T00:00:00';
        if (dateTo) exportRequest.to_date = dateTo + 'T23:59:59';
        
        const response = await apiRequest('/abac/audit-trail/batch-export', {
            method: 'POST',
            body: JSON.stringify(exportRequest)
        });
        
        if (response && response.task_id) {
            showToast(`Export task submitted! Task ID: ${response.task_id}`, 'success');
            
            // Poll for result
            pollBatchTaskStatus(response.task_id, 'export');
        }
    } catch (error) {
        console.error('Error submitting export task:', error);
        showToast('Failed to submit export task: ' + (error.message || 'Unknown error'), 'error');
    }
}

/**
 * Show export format selection dialog
 */
async function showExportFormatDialog() {
    return new Promise((resolve) => {
        const modal = document.createElement('div');
        modal.className = 'modal-overlay';
        modal.style.cssText = 'position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,0.5);display:flex;align-items:center;justify-content:center;z-index:10002;';
        modal.innerHTML = `
            <div style="background:white;border-radius:8px;padding:24px;max-width:300px;width:90%;">
                <h3 style="margin:0 0 16px 0;">Export Format</h3>
                <p style="color:#666;margin-bottom:16px;">Choose export format:</p>
                <div style="display:flex;gap:12px;justify-content:flex-end;">
                    <button class="btn btn-secondary" onclick="this.closest('.modal-overlay').remove();">Cancel</button>
                    <button class="btn btn-primary" id="exportJsonBtn">JSON</button>
                    <button class="btn btn-primary" id="exportCsvBtn">CSV</button>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
        
        modal.querySelector('#exportJsonBtn').onclick = () => { modal.remove(); resolve('json'); };
        modal.querySelector('#exportCsvBtn').onclick = () => { modal.remove(); resolve('csv'); };
        modal.onclick = (e) => { if (e.target === modal) { modal.remove(); resolve(null); } };
    });
}

/**
 * Show ABAC audit statistics using Celery batch processing
 */
async function showAbacAuditStatistics() {
    try {
        showToast('Loading statistics...', 'info');
        
        const response = await apiRequest('/abac/audit-trail/statistics');
        
        if (response) {
            showStatisticsModal(response);
        }
    } catch (error) {
        console.error('Error loading statistics:', error);
        showToast('Failed to load statistics: ' + (error.message || 'Unknown error'), 'error');
    }
}

/**
 * Display statistics in a modal
 */
function showStatisticsModal(stats) {
    const modal = document.createElement('div');
    modal.className = 'modal-overlay';
    modal.style.cssText = 'position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,0.5);display:flex;align-items:center;justify-content:center;z-index:10002;';
    
    const formatNumber = (num) => (num || 0).toLocaleString();
    
    modal.innerHTML = `
        <div style="background:white;border-radius:8px;padding:24px;max-width:500px;width:90%;">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:20px;">
                <h3 style="margin:0;">ABAC Audit Statistics</h3>
                <button style="background:none;border:none;font-size:20px;cursor:pointer;" onclick="this.closest('.modal-overlay').remove()">&times;</button>
            </div>
            
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:20px;">
                <div style="background:#e3f2fd;padding:16px;border-radius:8px;text-align:center;">
                    <div style="font-size:24px;font-weight:bold;color:#1976d2;">${formatNumber(stats.total_logs)}</div>
                    <div style="color:#666;font-size:0.9em;">Total Logs</div>
                </div>
                <div style="background:#e8f5e9;padding:16px;border-radius:8px;text-align:center;">
                    <div style="font-size:24px;font-weight:bold;color:#388e3c;">${formatNumber(stats.logs_last_24h)}</div>
                    <div style="color:#666;font-size:0.9em;">Last 24 Hours</div>
                </div>
                <div style="background:#fff3e0;padding:16px;border-radius:8px;text-align:center;">
                    <div style="font-size:24px;font-weight:bold;color:#f57c00;">${formatNumber(stats.logs_last_7d)}</div>
                    <div style="color:#666;font-size:0.9em;">Last 7 Days</div>
                </div>
                <div style="background:#fce4ec;padding:16px;border-radius:8px;text-align:center;">
                    <div style="font-size:24px;font-weight:bold;color:#c2185b;">${formatNumber(stats.logs_last_30d)}</div>
                    <div style="color:#666;font-size:0.9em;">Last 30 Days</div>
                </div>
            </div>
            
            ${stats.logs_by_action ? `
            <h4 style="margin:16px 0 8px 0;font-size:0.95em;">Logs by Action</h4>
            <div style="display:flex;flex-wrap:wrap;gap:8px;">
                ${Object.entries(stats.logs_by_action).map(([action, count]) => `
                    <span style="background:#f0f0f0;padding:4px 12px;border-radius:16px;font-size:0.85em;">
                        ${escapeHtml(action)}: <strong>${formatNumber(count)}</strong>
                    </span>
                `).join('')}
            </div>
            ` : ''}
            
            <div style="text-align:right;margin-top:20px;">
                <button class="btn btn-secondary" onclick="this.closest('.modal-overlay').remove()">Close</button>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    modal.onclick = (e) => { if (e.target === modal) modal.remove(); };
}

/**
 * Archive old ABAC audit logs using Celery batch processing
 */
async function archiveAbacAuditLogs() {
    // Show confirmation dialog with days input
    const days = await showArchiveConfirmDialog();
    if (!days) return; // User cancelled
    
    try {
        showToast('Submitting archive task...', 'info');
        
        const response = await apiRequest('/abac/audit-trail/batch-archive', {
            method: 'POST',
            body: JSON.stringify({ older_than_days: parseInt(days) })
        });
        
        if (response && response.task_id) {
            showToast(`Archive task submitted! Task ID: ${response.task_id}`, 'success');
            
            // Poll for result
            pollBatchTaskStatus(response.task_id, 'archive');
        }
    } catch (error) {
        console.error('Error submitting archive task:', error);
        showToast('Failed to submit archive task: ' + (error.message || 'Unknown error'), 'error');
    }
}

/**
 * Show archive confirmation dialog
 */
async function showArchiveConfirmDialog() {
    return new Promise((resolve) => {
        const modal = document.createElement('div');
        modal.className = 'modal-overlay';
        modal.style.cssText = 'position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,0.5);display:flex;align-items:center;justify-content:center;z-index:10002;';
        modal.innerHTML = `
            <div style="background:white;border-radius:8px;padding:24px;max-width:350px;width:90%;">
                <h3 style="margin:0 0 16px 0;">📦 Archive Old Logs</h3>
                <p style="color:#666;margin-bottom:16px;">Archive audit logs older than a specified number of days.</p>
                <div style="margin-bottom:16px;">
                    <label style="display:block;margin-bottom:4px;font-weight:500;">Days old:</label>
                    <input type="number" id="archiveDaysInput" value="90" min="1" max="365" 
                           style="width:100%;padding:8px;border:1px solid #ddd;border-radius:4px;">
                </div>
                <div style="display:flex;gap:12px;justify-content:flex-end;">
                    <button class="btn btn-secondary" onclick="this.closest('.modal-overlay').remove();">Cancel</button>
                    <button class="btn btn-warning" id="archiveConfirmBtn">Archive</button>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
        
        modal.querySelector('#archiveConfirmBtn').onclick = () => {
            const days = modal.querySelector('#archiveDaysInput').value;
            modal.remove();
            resolve(days);
        };
        modal.onclick = (e) => { if (e.target === modal) { modal.remove(); resolve(null); } };
    });
}

/**
 * Poll for batch task status
 */
async function pollBatchTaskStatus(taskId, taskType) {
    let attempts = 0;
    const maxAttempts = 30;
    
    const poll = async () => {
        attempts++;
        try {
            const status = await apiRequest(`/abac/audit-trail/batch-status/${taskId}`);
            
            if (status.status === 'SUCCESS') {
                showToast(`${taskType.charAt(0).toUpperCase() + taskType.slice(1)} completed successfully!`, 'success');
                
                // For export, try to download the result
                if (taskType === 'export') {
                    const result = await apiRequest(`/abac/audit-trail/batch-result/${taskId}`);
                    if (result && result.result) {
                        downloadExportResult(result.result);
                    }
                }
                return;
            }
            
            if (status.status === 'FAILURE') {
                showToast(`${taskType.charAt(0).toUpperCase() + taskType.slice(1)} failed: ${status.error || 'Unknown error'}`, 'error');
                return;
            }
            
            if (attempts < maxAttempts) {
                setTimeout(poll, 2000); // Poll every 2 seconds
            } else {
                showToast(`Task is taking longer than expected. Task ID: ${taskId}`, 'warning');
            }
        } catch (error) {
            console.error('Error polling task status:', error);
            if (attempts < maxAttempts) {
                setTimeout(poll, 2000);
            }
        }
    };
    
    poll();
}

/**
 * Download export result
 */
function downloadExportResult(result) {
    if (!result || !result.data) return;
    
    const format = result.format || 'json';
    const data = result.data;
    const blob = new Blob([format === 'json' ? JSON.stringify(data, null, 2) : data], {
        type: format === 'json' ? 'application/json' : 'text/csv'
    });
    
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `abac_audit_export_${new Date().toISOString().slice(0,10)}.${format}`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    showToast('Export downloaded successfully!', 'success');
}

// Close modal when clicking outside
window.addEventListener('click', (e) => {
    const modal = document.getElementById('auditTrailModal');
    if (e.target === modal) {
        closeAuditTrailModal();
    }
});
