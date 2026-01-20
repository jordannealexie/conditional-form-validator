// RBAC Management Module
// Handles role-based access control functionality using the real API

/**
 * Initialize roles page
 */
document.addEventListener('DOMContentLoaded', () => {
    if (typeof requireAuth === 'function') requireAuth();
    loadUserInfo();
    loadRoles();
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
 * Toggle the visibility of the add role form
 */
function toggleAddRoleForm() {
    const form = document.getElementById('addRoleForm');
    if (form) {
        form.style.display = form.style.display === 'none' ? 'block' : 'none';
    }
}

/**
 * Load and display all roles
 */
async function loadRoles() {
    try {
        const roles = await apiGetRoles();
        const tableBody = document.getElementById('rolesTableBody');
        if (!tableBody) return;

        tableBody.innerHTML = '';

        if (!roles || roles.length === 0) {
            tableBody.innerHTML = '<tr><td colspan="5" style="text-align: center;">No roles found</td></tr>';
            return;
        }

        roles.forEach(role => {
            const row = createRoleRow(role);
            tableBody.appendChild(row);
        });

        // Load permissions for the form
        loadPermissionsGrid();
    } catch (error) {
        console.error('Error loading roles:', error);
        showToast('Error loading roles', 'error');
    }
}

/**
 * Create a table row for a role
 * @param {object} role 
 * @returns {HTMLElement}
 */
function createRoleRow(role) {
    const row = document.createElement('tr');

    row.innerHTML = `
        <td>${role.name}</td>
        <td>${role.description || 'No description'}</td>
        <td>${(role.permissions || []).join(', ')}</td>
        <td><small>Check Users Tab</small></td>
        <td>
            <button class="btn btn-sm btn-primary" onclick="editRole(${role.id})">Edit</button>
            <button class="btn btn-sm btn-danger" onclick="deleteRole(${role.id})">Delete</button>
        </td>
    `;

    return row;
}

/**
 * Load permissions grid for role creation
 */
function loadPermissionsGrid() {
    const grid = document.getElementById('permissionsGrid');
    if (!grid) return;

    const allPermissions = [
        'users:read', 'users:write', 'users:delete',
        'roles:read', 'roles:write', 'roles:delete',
        'policies:read', 'policies:write', 'policies:delete',
        'relationships:read', 'relationships:write', 'relationships:delete',
        'system:configure'
    ];

    grid.innerHTML = allPermissions.map(perm => `
        <label class="checkbox-item" style="display: block; margin-bottom: 4px;">
            <input type="checkbox" value="${perm}" name="permissions">
            ${perm}
        </label>
    `).join('');
}

/**
 * Handle role creation form submission
 */
const addRoleForm = document.getElementById('addRoleForm');
if (addRoleForm) {
    addRoleForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const roleName = document.getElementById('roleName').value;
        const roleDescription = document.getElementById('roleDescription').value;

        // Get selected permissions
        const permissionCheckboxes = document.querySelectorAll('input[name="permissions"]:checked');
        const permissions = Array.from(permissionCheckboxes).map(cb => cb.value);

        try {
            await apiCreateRole({
                name: roleName,
                description: roleDescription,
                permissions: permissions
            });

            showToast('Role created successfully', 'success');
            e.target.reset();
            toggleAddRoleForm();
            loadRoles();
        } catch (error) {
            console.error('Error creating role:', error);
            showToast(error.message || 'Error creating role', 'error');
        }
    });
}

/**
 * Edit a role
 * @param {number} roleId 
 */
function editRole(roleId) {
    showToast('Role editing via API not fully implemented in UI yet', 'info');
}

/**
 * Delete a role
 * @param {number} roleId 
 */
async function deleteRole(roleId) {
    if (confirm('Are you sure you want to delete this role?')) {
        try {
            // Placeholder for deleteRole API
            showToast('Delete role API endpoint needs verification', 'info');
        } catch (error) {
            showToast('Error deleting role', 'error');
        }
    }
}
