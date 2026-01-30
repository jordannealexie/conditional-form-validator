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
                const value = escapeHtml(String(rule.value || ''));
                
                rulesDisplay += `
                    <div class="rule-badge">
                        <span class="rule-field">${escapeHtml(fieldLabel)}</span>
                        <span class="rule-operator">${escapeHtml(operatorLabel)}</span>
                        <span class="rule-value">${value}</span>
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
 * @param {string} [currentValue] - Current value for editing
 * @returns {string} HTML string for value input
 */
function buildValueInput(attrKey, currentValue = '') {
    const attr = getAttributeDefinition(attrKey);
    const escapedValue = escapeHtml(String(currentValue));
    
    if (!attr) {
        return `<input type="text" class="condition-value" placeholder="Enter value" value="${escapedValue}">`;
    }
    
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
            const values = cachedValueOptions[attrKey] || attr.static_values || [];
            
            if (values.length === 0) {
                // No values available - show loading indicator and fetch
                fetchAttributeValues(attrKey);
                return `
                    <select class="condition-value" data-attr-key="${escapeHtml(attrKey)}">
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
        const valueInput = condition.querySelector('.condition-value');
        const value = valueInput ? valueInput.value : '';

        if (field && operator && value !== '') {
            // Parse value to correct type based on attribute definition
            let parsedValue = value;
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
                    const valueInput = lastCondition.querySelector('.condition-value');
                    if (valueInput) {
                        valueInput.value = rule.value !== undefined ? String(rule.value) : '';
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
