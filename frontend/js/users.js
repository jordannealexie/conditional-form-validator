// User Management - Form Submission
// Edit, Delete, Add with Role; uses /users API

const ROLES = ['admin', 'supervisor', 'fieldman'];

document.addEventListener('DOMContentLoaded', () => {
    if (typeof requireAuth === 'function') requireAuth();
    loadUserInfo();
    loadUsers();
    setupMobileMenu();
    
    // Enforce UI permissions after a short delay
    if (typeof enforceUIPermissions === 'function') {
        setTimeout(enforceUIPermissions, 100);
    }
});

async function loadUserInfo() {
    try {
        const u = await apiGetCurrentUser();
        updateAppUserDisplay(u);
    } catch (e) { console.error('loadUserInfo', e); }
}

function setupMobileMenu() {
    const t = document.getElementById('menuToggle'), s = document.getElementById('sidebar');
    if (t && s) t.addEventListener('click', () => s.classList.toggle('active'));
}

async function loadUsers() {
    const tbody = document.getElementById('usersTableBody');
    if (!tbody) return;
    tbody.innerHTML = '<tr><td colspan="10" style="text-align:center;">Loading…</td></tr>';
    try {
        const users = await apiGetUsers();
        const list = Array.isArray(users) ? users : (users && users.data ? users.data : []);
        tbody.innerHTML = '';
        if (!list.length) {
            tbody.innerHTML = '<tr><td colspan="10" style="text-align:center;">No users found</td></tr>';
            return;
        }
        list.forEach(u => tbody.appendChild(createUserRow(u)));
    } catch (e) {
        console.error('loadUsers', e);
        tbody.innerHTML = '<tr><td colspan="10" style="text-align:center;color:var(--danger);">Error loading users</td></tr>';
        if (typeof showToast === 'function') showToast('Failed to load users', 'error');
    }
}

function createUserRow(user) {
    const tr = document.createElement('tr');
    tr.id = `user-row-${user.id}`;
    tr.dataset.userId = user.id;
    const roleCls = (user.user_role || '').toLowerCase() === 'admin' ? 'badge-primary' : (user.user_role ? 'badge-success' : 'badge-secondary');
    const roleHtml = user.user_role ? `<span class="badge ${roleCls}">${escapeHtml(user.user_role)}</span>` : '<span class="badge badge-secondary">—</span>';
    const statusHtml = user.active !== false ? '<span class="badge badge-success">Active</span>' : '<span class="badge badge-secondary">Inactive</span>';
    
    // Format audit fields from database
    const createdAt = user.created_at ? formatDateTime(user.created_at) : '-';
    const updatedAt = user.updated_at ? formatDateTime(user.updated_at) : '-';
    
    tr.innerHTML = `
        <td class="sticky-col"><strong>${escapeHtml(user.username)}</strong></td>
        <td>${user.id}</td>
        <td>${escapeHtml(user.email || '—')}</td>
        <td>${escapeHtml(user.department || '—')}</td>
        <td>${escapeHtml(user.location || '—')}</td>
        <td>${roleHtml}</td>
        <td>${statusHtml}</td>
        <td>${createdAt}</td>
        <td>${updatedAt}</td>
        <td class="table-actions">
            <button class="btn btn-sm btn-primary" onclick="editUser(${user.id})" data-permission="users" data-action="update">Edit</button>
            <button class="btn btn-sm btn-danger" onclick="deleteUser(${user.id}, '${escapeHtml(user.username).replace(/'/g, "\\'")}')" data-permission="users" data-action="delete">Delete</button>
        </td>
    `;
    return tr;
}

// Ensure loadUsers calls enforceUIPermissions after rendering
const originalLoadUsers = loadUsers;
loadUsers = async function () {
    await originalLoadUsers();
    if (typeof enforceUIPermissions === 'function') {
        enforceUIPermissions();
    }
};

function showAddUserModal() {
    const roleOpts = ROLES.map(r => `<option value="${r}">${r}</option>`).join('');
    const deptOpts = ['IT', 'Marketing', 'Finance', 'HR', 'Operations'].map(d => `<option value="${d}">${d}</option>`).join('');
    const locOpts = ['Parañaque', 'Makati', 'Quezon City'].map(l => `<option value="${l}">${l}</option>`).join('');
    const content = `
        <form id="addUserForm" onsubmit="handleAddUser(event)">
            <div class="field-row" style="display:flex; gap:10px;">
                <div class="form-group" style="flex:1;"><label>First Name</label><input type="text" name="first_name"></div>
                <div class="form-group" style="flex:1;"><label>Last Name</label><input type="text" name="last_name"></div>
            </div>
            <div class="form-group"><label>Username *</label><input type="text" name="username" required></div>
            <div class="form-group"><label>Email *</label><input type="email" name="email" required></div>
            <div class="form-group"><label>Password *</label><input type="password" name="password" required minlength="8"></div>
            <div class="form-group"><label>Role</label><select name="user_role">${roleOpts}</select></div>
            <div class="field-row" style="display:flex; gap:10px;">
                <div class="form-group" style="flex:1;"><label>Department</label><select name="department"><option value="">Select Department</option>${deptOpts}</select></div>
                <div class="form-group" style="flex:1;"><label>Location</label><select name="location"><option value="">Select Location</option>${locOpts}</select></div>
            </div>
        </form>
    `;
    createModal('Add New User', content, [
        { label: 'Cancel', type: 'secondary', onclick: 'closeModal()' },
        { label: 'Create', type: 'primary', onclick: "document.getElementById('addUserForm').requestSubmit()" }
    ]);
}

async function handleAddUser(ev) {
    ev.preventDefault();
    const fd = new FormData(ev.target);
    const username = (fd.get('username') || '').trim();
    const email = (fd.get('email') || '').trim();
    const password = (fd.get('password') || '').trim();

    if (!username || !email || !password) {
        showToast('Username, email, and password are required', 'error');
        return;
    }
    if (typeof isValidEmail === 'function' && !isValidEmail(email)) {
        showToast('Please enter a valid email', 'error');
        return;
    }
    if (password.length < 8) {
        showToast('Password must be at least 8 characters', 'error');
        return;
    }

    const payload = {
        username,
        email,
        password,
        first_name: fd.get('first_name') || null,
        last_name: fd.get('last_name') || null,
        user_role: fd.get('user_role'),
        department: fd.get('department') || null,
        location: fd.get('location') || null,
        bank_id: null
    };
    try {
        await apiCreateUser(payload);
        showToast('User created successfully', 'success');
        closeModal();
        await loadUsers(); // Reload users to show new user
    } catch (e) {
        showToast(e.message || 'Error creating user', 'error');
    }
}

async function editUser(userId) {
    try {
        const user = await apiGetUser(userId);
        if (!user) return;
        const roleOpts = ROLES.map(r => `<option value="${r}" ${(user.user_role || '') === r ? 'selected' : ''}>${r}</option>`).join('');
        const deptOpts = ['IT', 'Marketing', 'Finance', 'HR', 'Operations'].map(d => `<option value="${d}" ${(user.department || '') === d ? 'selected' : ''}>${d}</option>`).join('');
        const locOpts = ['Parañaque', 'Makati', 'Quezon City'].map(l => `<option value="${l}" ${(user.location || '') === l ? 'selected' : ''}>${l}</option>`).join('');
        const content = `
            <form id="editUserForm" onsubmit="handleEditUser(event, ${userId})">
                <div class="field-row" style="display:flex; gap:10px;">
                    <div class="form-group" style="flex:1;"><label>First Name</label><input type="text" name="first_name" value="${escapeHtml(user.first_name || '')}"></div>
                    <div class="form-group" style="flex:1;"><label>Last Name</label><input type="text" name="last_name" value="${escapeHtml(user.last_name || '')}"></div>
                </div>
                <div class="form-group"><label>Username</label><input type="text" name="username" value="${escapeHtml(user.username)}" readonly></div>
                <div class="form-group"><label>Email *</label><input type="email" name="email" value="${escapeHtml(user.email || '')}" required></div>
                <div class="form-group"><label>Role</label><select name="user_role">${roleOpts}</select></div>
                <div class="field-row" style="display:flex; gap:10px;">
                    <div class="form-group" style="flex:1;"><label>Department</label><select name="department"><option value="">Select Department</option>${deptOpts}</select></div>
                    <div class="form-group" style="flex:1;"><label>Location</label><select name="location"><option value="">Select Location</option>${locOpts}</select></div>
                </div>
                <div class="form-group"><label>Status</label><select name="active">
                    <option value="true" ${user.active !== false ? 'selected' : ''}>Active</option>
                    <option value="false" ${user.active === false ? 'selected' : ''}>Inactive</option>
                </select></div>
            </form>
        `;
        createModal('Edit User', content, [
            { label: 'Cancel', type: 'secondary', onclick: 'closeModal()' },
            { label: 'Save', type: 'primary', onclick: "document.getElementById('editUserForm').requestSubmit()" }
        ]);
    } catch (e) {
        showToast('Error loading user', 'error');
    }
}

async function handleEditUser(ev, userId) {
    ev.preventDefault();
    const fd = new FormData(ev.target);
    const email = (fd.get('email') || '').trim();
    if (!email) {
        showToast('Email is required', 'error');
        return;
    }
    if (typeof isValidEmail === 'function' && !isValidEmail(email)) {
        showToast('Please enter a valid email', 'error');
        return;
    }
    const payload = {
        email,
        first_name: fd.get('first_name') || null,
        last_name: fd.get('last_name') || null,
        user_role: fd.get('user_role'),
        department: fd.get('department') || null,
        location: fd.get('location') || null,
        active: fd.get('active') === 'true'
    };
    try {
        await apiUpdateUser(userId, payload);
        showToast('User updated successfully', 'success');
        closeModal();
        await loadUsers(); // Reload users to show changes
    } catch (e) {
        showToast(e.message || 'Error updating user', 'error');
    }
}

function deleteUser(userId, username) {
    const content = `<p>Are you sure you want to delete <strong>${escapeHtml(username)}</strong>?</p><p>This action cannot be undone.</p>`;
    createModal('Delete User', content, [
        { label: 'Cancel', type: 'secondary', onclick: 'closeModal()' },
        { label: 'Delete', type: 'danger', onclick: `confirmDeleteUser(${userId})` }
    ]);
}

async function confirmDeleteUser(userId) {
    try {
        await apiDeleteUser(userId);
        showToast('User deleted successfully', 'success');
        closeModal();
        loadUsers();
    } catch (e) {
        showToast(e.message || 'Error deleting user', 'error');
    }
}

