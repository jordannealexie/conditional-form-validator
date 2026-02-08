/**
 * Profile Module
 * Handles profile updates, password changes, and activity logs
 * Uses shared DropdownLoader for all dropdown values - NO HARDCODING
 */

document.addEventListener('DOMContentLoaded', () => {
    if (typeof requireAuth === 'function') requireAuth();
    loadUserInfo();
    initProfilePage();
    loadActivityLogs();
    setupMobileMenu();
});

/**
 * Initialize profile page - load dropdowns then user data
 */
async function initProfilePage() {
    try {
        // Load dropdown data using shared DropdownLoader
        await DropdownLoader.loadAll();
        
        // Populate dropdowns
        DropdownLoader.populateSelect('profile_department', 'departments', '', { emptyLabel: 'Select Department' });
        DropdownLoader.populateSelect('profile_location', 'locations', '', { emptyLabel: 'Select Location' });
        
        // Then load user profile data
        await loadProfileData();
    } catch (error) {
        console.error('Error initializing profile page:', error);
    }
}

/**
 * Load User Info for sidebar
 */
async function loadUserInfo() {
    try {
        const user = await apiGetCurrentUser();
        if (user) {
            document.getElementById('userName').textContent = user.username;
            document.getElementById('userRole').textContent = (user.roles || []).join(', ') || 'User';
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
            session.is_admin = user.is_superuser || user.user_role === 'admin';
            localStorage.setItem(SESSION_KEY, JSON.stringify(session));
        }

        // Re-enforce UI permissions after updating
        if (typeof enforceUIPermissions === 'function') {
            setTimeout(enforceUIPermissions, 100);
        }
    } catch (error) {
        console.error('Error loading user info:', error);
    }
}

/**
 * Load Profile Data into form
 */
async function loadProfileData() {
    try {
        const user = await apiGetCurrentUser();
        if (user) {
            document.getElementById('profile_username').value = user.username;
            document.getElementById('profile_email').value = user.email || '';
            document.getElementById('profile_first_name').value = user.first_name || '';
            document.getElementById('profile_last_name').value = user.last_name || '';

            // Set department dropdown value
            const deptSelect = document.getElementById('profile_department');
            if (user.department && deptSelect) {
                deptSelect.value = user.department;
            }

            // Set location dropdown value
            const locSelect = document.getElementById('profile_location');
            if (user.location && locSelect) {
                locSelect.value = user.location;
            }
        }
    } catch (error) {
        showToast('Error loading profile data', 'error');
    }
}

/**
 * Load User Activity Logs
 */
async function loadActivityLogs() {
    const tbody = document.getElementById('activityTableBody');
    if (!tbody) return;

    try {
        // Backend endpoint: GET /users/me/activity
        const response = await apiRequest('/users/me/activity');
        // Handle response format {data: [...]}
        const logs = response?.data || response || [];
        tbody.innerHTML = '';

        if (!logs || logs.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" style="text-align: center;">No recent activity</td></tr>';
            return;
        }

        logs.forEach(log => {
            const tr = document.createElement('tr');
            const time = new Date(log.created_at).toLocaleString();
            const statusClass = log.status === 'success' ? 'badge-success' : 'badge-danger';

            tr.innerHTML = `
                <td><strong>${log.action || 'N/A'}</strong></td>
                <td>${log.resource_type || 'N/A'}</td>
                <td><span class="badge ${statusClass}">${log.status || 'N/A'}</span></td>
                <td>${time}</td>
                <td>${log.details || ''}</td>
            `;
            tbody.appendChild(tr);
        });
    } catch (error) {
        console.error('Error loading activity logs:', error);
        tbody.innerHTML = '<tr><td colspan="5" style="text-align: center;">Error loading activity</td></tr>';
    }
}

/**
 * Handle Profile Update
 */
async function handleProfileUpdate(ev) {
    ev.preventDefault();
    const emailValue = (document.getElementById('profile_email')?.value || '').trim();
    if (!emailValue) {
        showToast('Email is required', 'error');
        return;
    }

    const firstNameValue = (document.getElementById('profile_first_name')?.value || '').trim();
    const lastNameValue = (document.getElementById('profile_last_name')?.value || '').trim();
    const departmentValue = (document.getElementById('profile_department')?.value || '').trim();
    const locationValue = (document.getElementById('profile_location')?.value || '').trim();

    const payload = {
        email: emailValue,
        first_name: firstNameValue ? firstNameValue : null,
        last_name: lastNameValue ? lastNameValue : null,
        department: departmentValue ? departmentValue : null,
        location: locationValue ? locationValue : null
    };
    try {
        const updated = await apiUpdateProfile(payload);
        if (typeof updateSession === 'function' && updated) {
            updateSession(updated);
        }
        showToast('Profile updated successfully', 'success');
        await loadProfileData(); // Reload profile to show changes
    } catch (e) {
        showToast(e.message || 'Error updating profile', 'error');
    }
}

/**
 * Handle Password Change
 */
async function handlePasswordChange(event) {
    event.preventDefault();

    const currentPass = document.getElementById('current_password').value;
    const newPass = document.getElementById('new_password').value;
    const confirmPass = document.getElementById('confirm_password').value;

    if (newPass !== confirmPass) {
        showToast('Passwords do not match', 'error');
        return;
    }

    try {
        await apiChangePassword({
            current_password: currentPass,
            new_password: newPass
        });
        showToast('Password changed successfully', 'success');
        event.target.reset();
    } catch (error) {
        showToast(error.message || 'Error changing password', 'error');
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
