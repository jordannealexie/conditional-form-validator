// User Management Module
// Handles user listing, creation, editing, and deletion using the real API

/**
 * Initialize the users page
 */
document.addEventListener('DOMContentLoaded', () => {
    if (typeof requireAuth === 'function') requireAuth();
    loadUserInfo();
    loadUsers();
    setupMobileMenu();
});

/**
 * Load current user info for the sidebar
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
 * Load and display all users from the real API
 */
async function loadUsers() {
    const tbody = document.getElementById('usersTableBody');
    if (!tbody) return;

    tbody.innerHTML = '<tr><td colspan="8" style="text-align: center;">Loading users...</td></tr>';

    try {
        const users = await apiGetUsers();
        tbody.innerHTML = '';

        if (!users || users.length === 0) {
            tbody.innerHTML = '<tr><td colspan="8" style="text-align: center;">No users found</td></tr>';
            return;
        }

        users.forEach(user => {
            const row = createUserRow(user);
            tbody.appendChild(row);
        });
    } catch (error) {
        console.error('Error loading users:', error);
        tbody.innerHTML = '<tr><td colspan="8" style="text-align: center; color: var(--danger);">Error loading users from server</td></tr>';
        showToast('Failed to load users from the server', 'error');
    }
}

/**
 * Create a table row for a user
 * @param {object} user 
 * @returns {HTMLElement}
 */
function createUserRow(user) {
    const tr = document.createElement('tr');

    const rolesHtml = (user.roles || []).map(role => {
        return `<span class="badge badge-primary">${role}</span>`;
    }).join(' ');

    const statusBadge = user.is_active
        ? '<span class="badge badge-success">Active</span>'
        : '<span class="badge badge-secondary">Inactive</span>';

    tr.innerHTML = `
        <td>${user.id}</td>
        <td><strong>${escapeHtml(user.username)}</strong></td>
        <td>${escapeHtml(user.full_name || 'N/A')}</td>
        <td>${escapeHtml(user.email || 'N/A')}</td>
        <td>${rolesHtml}</td>
        <td>${escapeHtml(user.attributes?.department || 'N/A')}</td>
        <td>${statusBadge}</td>
        <td class="table-actions">
            <button class="btn btn-sm btn-primary" onclick="editUser(${user.id})">
                Edit
            </button>
            <button class="btn btn-sm btn-warning" onclick="manageUserRoles(${user.id})">
                Roles
            </button>
            <button class="btn btn-sm btn-danger" onclick="deleteUser(${user.id})">
                Delete
            </button>
        </td>
    `;

    return tr;
}

/**
 * Show modal to add a new user
 */
function showAddUserModal() {
    const content = `
        <form id="addUserForm" onsubmit="handleAddUser(event)">
            <div class="form-row">
                <div class="form-group">
                    <label for="username">Username *</label>
                    <input type="text" id="username" name="username" required>
                </div>
                <div class="form-group">
                    <label for="email">Email *</label>
                    <input type="email" id="email" name="email" required>
                </div>
            </div>
            
            <div class="form-row">
                <div class="form-group">
                    <label for="first_name">First Name</label>
                    <input type="text" id="first_name" name="first_name">
                </div>
                <div class="form-group">
                    <label for="last_name">Last Name</label>
                    <input type="text" id="last_name" name="last_name">
                </div>
            </div>
            
            <div class="form-group">
                <label for="password">Password *</label>
                <input type="password" id="password" name="password" required>
            </div>
            
            <div class="form-row">
                <div class="form-group">
                    <label for="department">Department</label>
                    <input type="text" id="department" name="department" value="General">
                </div>
                <div class="form-group">
                    <label for="level">Level</label>
                    <input type="number" id="level" name="level" min="1" max="5" value="1">
                </div>
            </div>
        </form>
    `;

    createModal('Add New User', content, [
        { label: 'Cancel', type: 'secondary', onclick: 'closeModal()' },
        { label: 'Add User', type: 'primary', onclick: 'document.getElementById("addUserForm").requestSubmit()' }
    ]);
}

/**
 * Handle user creation
 */
async function handleAddUser(event) {
    event.preventDefault();

    const formData = new FormData(event.target);
    const userData = {
        username: formData.get('username'),
        email: formData.get('email'),
        first_name: formData.get('first_name'),
        last_name: formData.get('last_name'),
        password: formData.get('password'),
        attributes: {
            department: formData.get('department'),
            level: parseInt(formData.get('level'))
        }
    };

    try {
        await apiCreateUser(userData);
        showToast(`User ${userData.username} created successfully`, 'success');
        closeModal();
        loadUsers();
    } catch (error) {
        showToast(error.message || 'Error creating user', 'error');
    }
}

/**
 * Show modal to edit an existing user
 */
async function editUser(userId) {
    try {
        const user = await apiGetUser(userId);
        if (!user) return;

        const content = `
            <form id="editUserForm" onsubmit="handleEditUser(event, ${userId})">
                <div class="form-row">
                    <div class="form-group">
                        <label for="edit_username">Username</label>
                        <input type="text" id="edit_username" name="username" value="${escapeHtml(user.username)}" readonly>
                    </div>
                    <div class="form-group">
                        <label for="edit_email">Email</label>
                        <input type="email" id="edit_email" name="email" value="${escapeHtml(user.email)}" required>
                    </div>
                </div>
                
                <div class="form-row">
                    <div class="form-group">
                        <label for="edit_first_name">First Name</label>
                        <input type="text" id="edit_first_name" name="first_name" value="${escapeHtml(user.first_name || '')}">
                    </div>
                    <div class="form-group">
                        <label for="edit_last_name">Last Name</label>
                        <input type="text" id="edit_last_name" name="last_name" value="${escapeHtml(user.last_name || '')}">
                    </div>
                </div>
                
                <div class="form-row">
                    <div class="form-group">
                        <label for="edit_department">Department</label>
                        <input type="text" id="edit_department" name="department" value="${escapeHtml(user.attributes?.department || '')}">
                    </div>
                    <div class="form-group">
                        <label for="edit_is_active">Status</label>
                        <select id="edit_is_active" name="is_active">
                            <option value="true" ${user.is_active ? 'selected' : ''}>Active</option>
                            <option value="false" ${!user.is_active ? 'selected' : ''}>Inactive</option>
                        </select>
                    </div>
                </div>
            </form>
        `;

        createModal('Edit User', content, [
            { label: 'Cancel', type: 'secondary', onclick: 'closeModal()' },
            { label: 'Save Changes', type: 'primary', onclick: 'document.getElementById("editUserForm").requestSubmit()' }
        ]);
    } catch (error) {
        showToast('Error loading user data', 'error');
    }
}

/**
 * Handle user update
 */
async function handleEditUser(event, userId) {
    event.preventDefault();

    const formData = new FormData(event.target);
    const userData = {
        email: formData.get('email'),
        first_name: formData.get('first_name'),
        last_name: formData.get('last_name'),
        is_active: formData.get('is_active') === 'true',
        attributes: {
            department: formData.get('department')
        }
    };

    try {
        await apiUpdateUser(userId, userData);
        showToast('User updated successfully', 'success');
        closeModal();
        loadUsers();
    } catch (error) {
        showToast(error.message || 'Error updating user', 'error');
    }
}

/**
 * Show role management modal
 */
async function manageUserRoles(userId) {
    try {
        const [user, roles] = await Promise.all([
            apiGetUser(userId),
            apiGetRoles()
        ]);

        if (!user || !roles) return;

        const rolesCheckboxes = roles.map(role => {
            const checked = (user.roles || []).includes(role.name) ? 'checked' : '';
            return `
                <div style="padding: 8px;">
                    <label style="display: flex; align-items: center; gap: 8px; cursor: pointer;">
                        <input type="checkbox" name="roles" value="${role.name}" ${checked} 
                               onchange="handleToggleRole('${user.username}', '${role.name}', this)">
                        <span>${role.name}</span>
                        <small style="color: var(--gray-500)">${role.description || ''}</small>
                    </label>
                </div>
            `;
        }).join('');

        const content = `
            <div>
                <p style="margin-bottom: 16px; color: var(--gray-600);">Manage roles for <strong>${escapeHtml(user.username)}</strong>:</p>
                <div id="rolesList">
                    ${rolesCheckboxes}
                </div>
            </div>
        `;

        createModal('Manage User Roles', content, [
            { label: 'Close', type: 'secondary', onclick: 'closeModal(); loadUsers();' }
        ]);
    } catch (error) {
        showToast('Error loading roles data', 'error');
    }
}

/**
 * Handle individual role toggling
 */
async function handleToggleRole(username, roleName, checkbox) {
    try {
        if (checkbox.checked) {
            await apiAssignRole(username, roleName);
            showToast(`Role ${roleName} assigned`, 'success');
        } else {
            await apiRevokeRole(username, roleName);
            showToast(`Role ${roleName} revoked`, 'success');
        }
    } catch (error) {
        checkbox.checked = !checkbox.checked; // Revert checkbox
        showToast(error.message || 'Error updating role', 'error');
    }
}

/**
 * Handle user deletion
 */
async function deleteUser(userId) {
    try {
        const user = await apiGetUser(userId);
        if (!user) return;

        const confirmed = await confirm(`Are you sure you want to delete user "${user.username}"?`);
        if (!confirmed) return;

        await apiDeleteUser(userId);
        showToast(`User ${user.username} deleted successfully`, 'success');
        loadUsers();
    } catch (error) {
        showToast(error.message || 'Error deleting user', 'error');
    }
}
