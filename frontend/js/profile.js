/**
 * Profile Module
 * Handles profile updates, password changes, and activity logs
 */

document.addEventListener('DOMContentLoaded', () => {
    if (typeof requireAuth === 'function') requireAuth();
    loadUserInfo();
    loadProfileData();
    loadActivityLogs();
    setupMobileMenu();
});

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
            
            // Set department dropdown
            const deptSelect = document.getElementById('profile_department');
            if (user.department && deptSelect) {
                deptSelect.value = user.department;
            }
            
            // Set location dropdown
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
async function handleProfileUpdate(event) {
    event.preventDefault();

    const userData = {
        email: document.getElementById('profile_email').value,
        first_name: document.getElementById('profile_first_name').value,
        last_name: document.getElementById('profile_last_name').value,
        department: document.getElementById('profile_department').value,
        location: document.getElementById('profile_location').value
    };

    try {
        await apiRequest('/users/me', {
            method: 'PATCH',
            body: userData
        });
        showToast('Profile updated successfully', 'success');
    } catch (error) {
        showToast(error.message || 'Error updating profile', 'error');
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
        await apiRequest('/users/me/password', {
            method: 'POST',
            body: {
                current_password: currentPass,
                new_password: newPass
            }
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
