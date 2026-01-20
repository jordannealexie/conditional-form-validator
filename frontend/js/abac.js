// ABAC Management Module
// Handles attribute-based access control functionality using the real API

/**
 * Initialize ABAC page
 */
document.addEventListener('DOMContentLoaded', () => {
    if (typeof requireAuth === 'function') requireAuth();
    loadUserInfo();
    loadPolicies();
    setupMobileMenu();
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
        form.style.display = form.style.display === 'none' ? 'block' : 'none';
    }
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

    row.innerHTML = `
        <td>${policy.name}</td>
        <td>${policy.resource || 'All'}</td>
        <td>${policy.action || 'All'}</td>
        <td><code>${policy.rule}</code></td>
        <td>
            <button class="btn btn-sm btn-primary" onclick="editPolicy(${policy.id})">Edit</button>
            <button class="btn btn-sm btn-danger" onclick="deletePolicy(${policy.id})">Delete</button>
            <button class="btn btn-sm btn-info" onclick="testPolicy(${policy.id})">Test</button>
        </td>
    `;

    return row;
}

/**
 * Handle policy creation
 */
const addPolicyForm = document.getElementById('addPolicyForm');
if (addRoleForm) {
    addPolicyForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const policyName = document.getElementById('policyName').value;
        const policyDescription = document.getElementById('policyDescription').value;
        const resource = document.getElementById('resource').value;
        const action = document.getElementById('action').value;

        // Build rule from conditions
        const rule = buildPolicyRule();

        try {
            await apiCreatePolicy({
                name: policyName,
                description: policyDescription,
                resource: resource,
                action: action,
                rule: rule,
                effect: 'allow',
                priority: 1
            });

            showToast('Policy created successfully', 'success');
            e.target.reset();
            toggleAddPolicyForm();
            loadPolicies();
        } catch (error) {
            console.error('Error creating policy:', error);
            showToast(error.message || 'Error creating policy', 'error');
        }
    });
}

/**
 * Add a condition to the policy builder
 */
function addCondition() {
    const conditionsBuilder = document.getElementById('conditionsBuilder');

    const conditionDiv = document.createElement('div');
    conditionDiv.className = 'condition-item';
    conditionDiv.style.display = 'flex';
    conditionDiv.style.gap = '8px';
    conditionDiv.style.marginBottom = '8px';

    conditionDiv.innerHTML = `
        <select class="condition-attribute" style="flex: 1;">
            <option value="">Select Attribute</option>
            <option value="user.department">User Department</option>
            <option value="user.level">User Level</option>
            <option value="user.clearance">User Clearance</option>
            <option value="resource.department">Resource Department</option>
            <option value="resource.level">Resource Level</option>
        </select>
        <select class="condition-operator">
            <option value="==">==</option>
            <option value="!=">!=</option>
            <option value=">">&gt;</option>
            <option value="<">&lt;</option>
            <option value=">=">&gt;=</option>
            <option value="<=">&lt;=</option>
        </select>
        <input type="text" class="condition-value" placeholder="Value" style="flex: 1;">
        <button type="button" class="btn btn-sm btn-danger" onclick="removeCondition(this)">×</button>
    `;

    conditionsBuilder.appendChild(conditionDiv);
}

/**
 * Remove a condition
 */
function removeCondition(button) {
    button.parentElement.remove();
}

/**
 * Build policy rule from conditions
 */
function buildPolicyRule() {
    const conditions = document.querySelectorAll('.condition-item');
    const rules = [];

    conditions.forEach(condition => {
        const attribute = condition.querySelector('.condition-attribute').value;
        const operator = condition.querySelector('.condition-operator').value;
        const value = condition.querySelector('.condition-value').value;

        if (attribute && operator && value) {
            // Check if value is number
            const formattedValue = isNaN(value) ? `"${value}"` : value;
            rules.push(`${attribute} ${operator} ${formattedValue}`);
        }
    });

    return rules.join(' && ') || 'true';
}

/**
 * Placeholder for policy editing
 */
function editPolicy(policyId) {
    showToast('Policy editing not implemented in UI yet', 'info');
}

/**
 * Delete a policy
 */
async function deletePolicy(policyId) {
    if (confirm('Are you sure you want to delete this policy?')) {
        try {
            // Placeholder for deletePolicy API
            showToast('Delete policy API needs verification', 'info');
        } catch (error) {
            showToast('Error deleting policy', 'error');
        }
    }
}

/**
 * Test a policy
 */
function testPolicy(policyId) {
    showToast('Policy testing not implemented in UI yet', 'info');
}
