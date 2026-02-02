// User Management - Form Submission
// Edit, Delete, Add with Role; uses /users API
// Uses shared DropdownLoader for all dropdown values - NO HARDCODING

document.addEventListener('DOMContentLoaded', () => {
    if (typeof requireAuth === 'function') requireAuth();
    loadUserInfo();
    initUserManagement();
    setupMobileMenu();
    
    // Enforce UI permissions after a short delay
    if (typeof enforceUIPermissions === 'function') {
        setTimeout(enforceUIPermissions, 100);
    }
});

/**
 * Initialize user management - load dropdowns then users
 */
async function initUserManagement() {
    try {
        console.log('[users.js] initUserManagement started, DropdownLoader:', typeof DropdownLoader);
        // Load dropdown data first using shared DropdownLoader
        await DropdownLoader.loadAll();
        console.log('[users.js] DropdownLoader.loadAll() completed');
        // Then load users
        await loadUsers();
    } catch (error) {
        console.error('Error initializing user management:', error);
    }
}

/**
 * Build role options HTML using DropdownLoader
 * @param {string} [selectedRole] - Currently selected role
 * @returns {string} HTML options string
 */
function buildRoleOptions(selectedRole = '') {
    console.log('[users.js] buildRoleOptions called, DropdownLoader:', typeof DropdownLoader);
    const options = DropdownLoader.buildOptions('roles', selectedRole, { emptyLabel: 'Select Role' });
    console.log('[users.js] Role options built:', options.substring(0, 100));
    return options;
}

/**
 * Build department options HTML using DropdownLoader
 * @param {string} [selectedDept] - Currently selected department
 * @returns {string} HTML options string
 */
function buildDepartmentOptions(selectedDept = '') {
    return DropdownLoader.buildOptions('departments', selectedDept, { emptyLabel: 'Select Department' });
}

/**
 * Build location options HTML using DropdownLoader
 * @param {string} [selectedLoc] - Currently selected location
 * @returns {string} HTML options string
 */
function buildLocationOptions(selectedLoc = '') {
    return DropdownLoader.buildOptions('locations', selectedLoc, { emptyLabel: 'Select Location' });
}

/**
 * Build level options HTML using DropdownLoader
 * @param {number|string} [selectedLevel] - Currently selected level
 * @returns {string} HTML options string
 */
function buildLevelOptions(selectedLevel = '') {
    return DropdownLoader.buildOptions('levels', selectedLevel, { emptyLabel: 'Select Level' });
}

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
    const roleOpts = buildRoleOptions();
    const deptOpts = buildDepartmentOptions();
    const locOpts = buildLocationOptions();
    const levelOpts = buildLevelOptions('1'); // Default to Level 1
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
                <div class="form-group" style="flex:1;"><label>Department</label><select name="department">${deptOpts}</select></div>
                <div class="form-group" style="flex:1;"><label>Location</label><select name="location">${locOpts}</select></div>
            </div>
            <div class="form-group"><label>Level</label><select name="level">${levelOpts}</select></div>
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
        user_role: fd.get('user_role') || null,
        department: fd.get('department') || null,
        location: fd.get('location') || null,
        level: parseInt(fd.get('level')) || 1,
        bank_id: null
    };
    try {
        const newUser = await apiCreateUser(payload);
        showToast('User created successfully', 'success');
        closeModal();
        
        // Add new user to the table immediately
        if (newUser) {
            const tbody = document.getElementById('usersTableBody');
            if (tbody) {
                // Remove "no users" message if present
                const noDataRow = tbody.querySelector('td[colspan]');
                if (noDataRow) {
                    noDataRow.parentElement.remove();
                }
                // Append new user row
                tbody.appendChild(createUserRow(newUser));
                // Re-apply permissions after adding row
                if (typeof enforceUIPermissions === 'function') {
                    enforceUIPermissions();
                }
            }
        }
    } catch (e) {
        showToast(e.message || 'Error creating user', 'error');
    }
}

async function editUser(userId) {
    try {
        const user = await apiGetUser(userId);
        if (!user) return;
        const roleOpts = buildRoleOptions(user.user_role || '');
        const deptOpts = buildDepartmentOptions(user.department || '');
        const locOpts = buildLocationOptions(user.location || '');
        const levelOpts = buildLevelOptions(user.level || 1);
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
                    <div class="form-group" style="flex:1;"><label>Department</label><select name="department">${deptOpts}</select></div>
                    <div class="form-group" style="flex:1;"><label>Location</label><select name="location">${locOpts}</select></div>
                </div>
                <div class="field-row" style="display:flex; gap:10px;">
                    <div class="form-group" style="flex:1;"><label>Level</label><select name="level">${levelOpts}</select></div>
                    <div class="form-group" style="flex:1;"><label>Status</label><select name="active">
                        <option value="true" ${user.active !== false ? 'selected' : ''}>Active</option>
                        <option value="false" ${user.active === false ? 'selected' : ''}>Inactive</option>
                    </select></div>
                </div>
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
        user_role: fd.get('user_role') || null,
        department: fd.get('department') || null,
        location: fd.get('location') || null,
        level: parseInt(fd.get('level')) || 1,
        active: fd.get('active') === 'true'
    };
    try {
        const updatedUser = await apiUpdateUser(userId, payload);
        showToast('User updated successfully', 'success');
        closeModal();
        
        // Update the specific row immediately with response data
        if (updatedUser) {
            const existingRow = document.getElementById(`user-row-${userId}`);
            if (existingRow) {
                const newRow = createUserRow(updatedUser);
                existingRow.replaceWith(newRow);
                // Re-apply permissions after row update
                if (typeof enforceUIPermissions === 'function') {
                    enforceUIPermissions();
                }
            }
        }
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

/**
 * Show audit trail modal for all users
 */
async function showAuditTrail() {
    const content = `
        <div class="audit-trail-container">
            <p class="audit-trail-subtitle">User Management Audit Trail - All Activities</p>
            <div id="auditTrailLoading" style="text-align: center; padding: 20px;">
                <p>Loading audit logs...</p>
            </div>
            <div id="auditTrailContent" style="display: none;">
                <div class="table-wrapper" style="max-height: 500px; overflow-y: auto;">
                    <table class="audit-table" style="width: 100%;">
                        <thead>
                            <tr>
                                <th>User</th>
                                <th>Action</th>
                                <th>Date/Time</th>
                                <th>Performed By</th>
                                <th>Changes</th>
                            </tr>
                        </thead>
                        <tbody id="auditTrailTableBody">
                        </tbody>
                    </table>
                </div>
            </div>
            <div id="auditTrailError" style="display: none; text-align: center; padding: 20px; color: var(--danger);">
                <p>Failed to load audit trail</p>
            </div>
        </div>
    `;
    
    createModal('User Management Audit Trail', content, [
        { label: 'Close', type: 'secondary', onclick: 'closeModal()' }
    ], 'large');
    
    // Load audit trail data
    await loadAuditTrail();
}

/**
 * Load and display audit trail for all users
 */
async function loadAuditTrail() {
    const loading = document.getElementById('auditTrailLoading');
    const content = document.getElementById('auditTrailContent');
    const error = document.getElementById('auditTrailError');
    const tbody = document.getElementById('auditTrailTableBody');
    
    try {
        const response = await apiGetAllAuditLogs(0, 100);
        
        if (loading) loading.style.display = 'none';
        
        // Handle null or empty response
        const logs = Array.isArray(response) ? response : [];
        
        if (logs.length === 0) {
            if (tbody) {
                tbody.innerHTML = '<tr><td colspan="5" style="text-align: center; padding: 20px;">No audit logs found</td></tr>';
            }
            if (content) content.style.display = 'block';
            return;
        }
        
        // Populate audit trail table
        tbody.innerHTML = '';
        logs.forEach(log => {
            const tr = document.createElement('tr');
            
            // Format user
            const targetUser = log.username ? escapeHtml(log.username) : (log.resource_id ? `User ID: ${log.resource_id}` : '-');
            
            // Format action
            let actionLabel = log.action || 'Unknown';
            let actionBadge = 'badge-secondary';
            if (actionLabel.includes('created')) {
                actionLabel = 'Created';
                actionBadge = 'badge-success';
            } else if (actionLabel.includes('updated')) {
                actionLabel = 'Updated';
                actionBadge = 'badge-primary';
            } else if (actionLabel.includes('deleted')) {
                actionLabel = 'Deleted';
                actionBadge = 'badge-danger';
            }
            
            // Format date/time
            const dateTime = log.created_at ? formatDateTime(log.created_at) : '-';
            
            // Format performed by
            let performedBy = '-';
            if (log.created_by) {
                performedBy = `User ID: ${log.created_by}`;
            } else if (log.updated_by) {
                performedBy = `User ID: ${log.updated_by}`;
            } else if (log.deleted_by) {
                performedBy = `User ID: ${log.deleted_by}`;
            } else if (log.user_id) {
                performedBy = `User ID: ${log.user_id}`;
            }
            
            // Format changes (JSON)
            let changesHtml = '-';
            if (log.changes && typeof log.changes === 'object') {
                changesHtml = `<button class="btn btn-sm btn-info" onclick="showChangesDetail(${escapeHtml(JSON.stringify(log.changes).replace(/"/g, '&quot;'))})">View Changes</button>`;
            }
            
            tr.innerHTML = `
                <td>${targetUser}</td>
                <td><span class="badge ${actionBadge}">${actionLabel}</span></td>
                <td>${dateTime}</td>
                <td>${performedBy}</td>
                <td>${changesHtml}</td>
            `;
            
            tbody.appendChild(tr);
        });
        
        if (content) content.style.display = 'block';
        
    } catch (e) {
        console.error('Error loading audit trail:', e);
        if (loading) loading.style.display = 'none';
        if (error) error.style.display = 'block';
        if (typeof showToast === 'function') {
            showToast('Failed to load audit trail', 'error');
        }
    }
}

/**
 * Show detailed changes in a modal
 * @param {object} changes - Changes object
 */
function showChangesDetail(changes) {
    let content = '<div class="changes-detail">';
    
    if (changes.action) {
        content += `<p><strong>Action:</strong> ${escapeHtml(changes.action)}</p>`;
    }
    
    if (changes.before) {
        content += '<div style="margin-top: 15px;"><strong>Before:</strong><pre style="background: #f5f5f5; padding: 10px; border-radius: 4px; max-height: 300px; overflow-y: auto;">' + escapeHtml(JSON.stringify(changes.before, null, 2)) + '</pre></div>';
    }
    
    if (changes.after) {
        content += '<div style="margin-top: 15px;"><strong>After:</strong><pre style="background: #f5f5f5; padding: 10px; border-radius: 4px; max-height: 300px; overflow-y: auto;">' + escapeHtml(JSON.stringify(changes.after, null, 2)) + '</pre></div>';
    }
    
    content += '</div>';
    
    createModal('Change Details', content, [
        { label: 'Close', type: 'secondary', onclick: 'closeModal()' }
    ], 'large');
}


