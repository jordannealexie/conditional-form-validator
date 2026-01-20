// Dashboard Module
// Handles dashboard statistics and user overview using the real API

/**
 * Initialize the dashboard
 */
document.addEventListener('DOMContentLoaded', () => {
    if (typeof requireAuth === 'function') requireAuth();
    loadDashboard();
    setupMobileMenu();
});

/**
 * Load dashboard statistics from the real API
 */
async function loadDashboard() {
    try {
        const currentUser = await apiGetCurrentUser();
        if (!currentUser) {
            window.location.href = 'index.html';
            return;
        }

        // Update user info in sidebar
        document.getElementById('userName').textContent = currentUser.full_name || currentUser.username;
        document.getElementById('userRole').textContent = currentUser.roles?.join(', ') || 'User';

        // Update system info section
        document.getElementById('currentUserName').textContent = currentUser.username;
        document.getElementById('currentUserRoles').textContent = currentUser.roles?.join(', ') || 'None';
        document.getElementById('currentUserDept').textContent = currentUser.department || 'N/A';
        document.getElementById('currentUserLevel').textContent = currentUser.level || 'N/A';

        // Fetch counts from various APIs
        const [users, roles, policies, relationships] = await Promise.all([
            apiGetUsers().catch(() => []),
            apiGetRoles().catch(() => []),
            apiGetPolicies().catch(() => []),
            apiGetRelationships().catch(() => [])
        ]);

        // Update stats cards
        document.getElementById('totalUsers').textContent = users.length;
        document.getElementById('totalRoles').textContent = roles.length;
        document.getElementById('totalPolicies').textContent = policies.length;
        document.getElementById('totalRelationships').textContent = relationships.length;

    } catch (error) {
        console.error('Error loading dashboard data:', error);
        showToast('Error loading some dashboard statistics', 'warning');
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
