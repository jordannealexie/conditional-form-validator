// ABAC Management Module
// Handles attribute-based access control functionality using the real API

let availableAttributes = null;

/**
 * Initialize ABAC page
 */
document.addEventListener('DOMContentLoaded', async () => {
    if (typeof requireAuth === 'function') requireAuth();
    loadUserInfo();
    
    // Load available attributes first
    try {
        availableAttributes = await apiGetAbacAttributes();
    } catch (error) {
        console.error('Error loading ABAC attributes:', error);
    }
    
    loadPolicies();
    setupMobileMenu();
    
    // Enforce UI permissions after a short delay to ensure everything is loaded
    if (typeof enforceUIPermissions === 'function') {
        setTimeout(enforceUIPermissions, 100);
    }
});

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
            // Hide and reset
            form.style.display = 'none';
            resetPolicyForm();
        } else {
            // Show
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
            tableBody.innerHTML = '<tr><td colspan="5" style="text-align: center;">No policies found</td></tr>';
            return;
        }

        policies.forEach(policy => {
            const row = createPolicyRow(policy);
            tableBody.appendChild(row);
        });
        
        // Enforce permissions after loading
        if (typeof enforceUIPermissions === 'function') {
            enforceUIPermissions();
        }
    } catch (error) {
        console.error('Error loading policies:', error);
        showToast('Error loading policies', 'error');
    }
}

/**
 * Create a table row for a policy
 * @param {object} policy 
 * @returns {HTMLElement}
 */
function createPolicyRow(policy) {
    const row = document.createElement('tr');
    
    // Format rules as badges
    let rulesDisplay = '<div class="policy-rule-display">';
    if (policy.rules && policy.rules.rules && Array.isArray(policy.rules.rules)) {
        if (policy.rules.rules.length === 0) {
            rulesDisplay += '<span class="badge badge-info">No conditions</span>';
        } else {
            policy.rules.rules.forEach(rule => {
                const field = escapeHtml(String(rule.field || ''));
                const operator = escapeHtml(String(rule.operator || ''));
                const value = escapeHtml(String(rule.value || ''));
                
                rulesDisplay += `
                    <div class="rule-badge">
                        <span class="rule-field">${field}</span>
                        <span class="rule-operator">${operator}</span>
                        <span class="rule-value">${value}</span>
                    </div>
                `;
            });
        }
    } else {
        rulesDisplay += '<span class="badge badge-info">No conditions</span>';
    }
    rulesDisplay += '</div>';
    
    const statusBadge = policy.is_active ? '<span class="badge badge-success">Active</span>' : '<span class="badge badge-secondary">Inactive</span>';
    
    const createdAt = policy.created_at ? new Date(policy.created_at).toLocaleString('en-US', {month: 'short', day: 'numeric', year: 'numeric', hour: '2-digit', minute: '2-digit'}) : 'N/A';
    const updatedAt = policy.updated_at ? new Date(policy.updated_at).toLocaleString('en-US', {month: 'short', day: 'numeric', year: 'numeric', hour: '2-digit', minute: '2-digit'}) : 'N/A';

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

        // Build rules from conditions
        const rules = buildPolicyRules();
        
        // Validate that at least one condition is added
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
                // Update existing policy
                await apiUpdatePolicy(parseInt(editId), policyData);
                showToast('Policy updated successfully', 'success');
            } else {
                // Create new policy
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
    
    // Reset conditions
    const conditionsBuilder = document.getElementById('conditionsBuilder');
    conditionsBuilder.innerHTML = '<div class="empty-state" id="emptyRulesState"><p>No conditions added yet. Click "Add Condition" to start.</p></div>';
    
    // Reset button text and form title
    const submitBtn = form.querySelector('button[type="submit"]');
    if (submitBtn) submitBtn.textContent = 'Create Policy';
    
    const formTitle = document.getElementById('formTitle');
    if (formTitle) formTitle.textContent = 'Add New Policy';
}

/**
 * Add a condition to the policy builder
 */
function addCondition() {
    const conditionsBuilder = document.getElementById('conditionsBuilder');
    
    // Hide empty state if it exists
    const emptyState = document.getElementById('emptyRulesState');
    if (emptyState) {
        emptyState.style.display = 'none';
    }

    const conditionDiv = document.createElement('div');
    conditionDiv.className = 'condition-item';

    // Build attribute options from available attributes
    let attributeOptions = '<option value="">Select Attribute</option>';
    
    if (availableAttributes) {
        // Add user attributes
        if (availableAttributes.user_attributes) {
            attributeOptions += '<optgroup label="User Attributes">';
            availableAttributes.user_attributes.forEach(attr => {
                attributeOptions += `<option value="${escapeHtml(attr.key)}">${escapeHtml(attr.label)}</option>`;
            });
            attributeOptions += '</optgroup>';
        }
        
        // Add resource attributes
        if (availableAttributes.resource_attributes) {
            attributeOptions += '<optgroup label="Resource Attributes">';
            availableAttributes.resource_attributes.forEach(attr => {
                attributeOptions += `<option value="${escapeHtml(attr.key)}">${escapeHtml(attr.label)}</option>`;
            });
            attributeOptions += '</optgroup>';
        }
    } else {
        // Fallback to static options if API data not loaded
        attributeOptions += `
            <optgroup label="User Attributes">
                <option value="user.user_role">User Role</option>
                <option value="user.department">Department</option>
                <option value="user.level">Level</option>
                <option value="user.location">Location</option>
                <option value="user.bank_id">Bank ID</option>
            </optgroup>
            <optgroup label="Resource Attributes">
                <option value="resource.user_id">Resource Owner ID</option>
                <option value="resource.bank_id">Resource Bank ID</option>
                <option value="resource.status">Status</option>
                <option value="resource.classification">Classification</option>
            </optgroup>
        `;
    }

    conditionDiv.innerHTML = `
        <div class="form-group">
            <label>Attribute</label>
            <select class="condition-attribute">
                ${attributeOptions}
            </select>
        </div>
        <div class="form-group">
            <label>Operator</label>
            <select class="condition-operator">
                <option value="==">Equals (==)</option>
                <option value="!=">Not Equals (!=)</option>
                <option value=">">Greater Than (>)</option>
                <option value="<">Less Than (<)</option>
                <option value=">=">Greater or Equal (>=)</option>
                <option value="<=">Less or Equal (<=)</option>
                <option value="contains">Contains</option>
                <option value="in">In List</option>
            </select>
        </div>
        <div class="form-group">
            <label>Value</label>
            <input type="text" class="condition-value" placeholder="Enter value">
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
    
    // Show empty state if no conditions remain
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
        const value = condition.querySelector('.condition-value').value;

        if (field && operator && value) {
            // Parse value to correct type
            let parsedValue = value;
            if (!isNaN(value) && value !== '') {
                parsedValue = Number(value);
            } else if (value.toLowerCase() === 'true') {
                parsedValue = true;
            } else if (value.toLowerCase() === 'false') {
                parsedValue = false;
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
        conditionsBuilder.innerHTML = '<div class="empty-state" id="emptyRulesState"><p>No conditions added yet. Click "Add Condition" to start.</p></div>';

        if (policy.rules && policy.rules.rules && Array.isArray(policy.rules.rules) && policy.rules.rules.length > 0) {
            policy.rules.rules.forEach(rule => {
                addCondition();
                const lastCondition = conditionsBuilder.lastElementChild;
                lastCondition.querySelector('.condition-attribute').value = rule.field || '';
                lastCondition.querySelector('.condition-operator').value = rule.operator || '==';
                lastCondition.querySelector('.condition-value').value = rule.value || '';
            });
        }

        // Show form if hidden
        const form = document.getElementById('addPolicyForm');
        if (form.style.display === 'none') {
            form.style.display = 'block';
        }
        
        // Change form to edit mode
        form.dataset.editId = policyId;
        
        // Change button text and header
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
