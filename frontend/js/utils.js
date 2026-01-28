// Utility Functions
// Helper functions for common tasks

/**
 * Show toast notification
 * @param {string} message 
 * @param {string} type - success, error, warning, info
 * @param {number} duration - milliseconds
 */
function showToast(message, type = 'info', duration = 3000) {
    const container = document.getElementById('toastContainer') || createToastContainer();

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        <span>${getToastIcon(type)}</span>
        <span>${message}</span>
    `;

    container.appendChild(toast);

    // Auto remove after duration
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100%)';
        setTimeout(() => toast.remove(), 300);
    }, duration);
}

/**
 * Globally show access denied message
 * @param {string} message 
 */
function showAccessDeniedMessage(message) {
    // Use non-blocking toast notification instead of modal
    // This provides subtle feedback without interrupting user flow
    if (typeof showToast === 'function') {
        showToast(message, 'warning');
    } else {
        console.warn('Access Denied:', message);
    }
}

/**
 * Scan DOM for data-permission and data-action attributes and hide elements
 * that the user is not authorized for.
 */
function enforceUIPermissions() {
    if (typeof hasPermission !== 'function') return;

    const elements = document.querySelectorAll('[data-permission]');
    elements.forEach(el => {
        const resource = el.getAttribute('data-permission');
        const action = el.getAttribute('data-action') || 'read'; // Default action is read

        if (!hasPermission(resource, action)) {
            el.style.display = 'none';
            el.classList.add('permission-hidden');

            // If it's a link or button, disable it just in case
            if (el.tagName === 'A' || el.tagName === 'BUTTON') {
                el.disabled = true;
                el.setAttribute('disabled', 'disabled');
                el.onclick = (e) => {
                    e.preventDefault();
                    showAccessDeniedMessage(`You do not have permission to ${action} ${resource}.`);
                    return false;
                };
            }
        }
    });

    // Also handle direct URL access protection
    protectCurrentPage();
}

/**
 * Protect specific pages based on metadata or path
 */
function protectCurrentPage() {
    const path = window.location.pathname;
    const user = getCurrentUser();
    if (!user) return; // auth.js handleAuth will redirect anyway

    // List of pages and required permissions
    const routePermissions = {
        'users.html': { resource: 'users', action: 'read' },
        'roles.html': { resource: 'roles', action: 'read' },
        'admin-templates.html': { resource: 'templates', action: 'read' },
        'submissions.html': { resource: 'submissions', action: 'read' },
        'abac.html': { resource: 'policies', action: 'read' },
        'rebac.html': { resource: 'relationships', action: 'read' }
    };

    for (const [page, perm] of Object.entries(routePermissions)) {
        if (path.includes(page)) {
            if (!hasPermission(perm.resource, perm.action)) {
                console.warn(`Redirecting unauthorized access to ${page}`);
                // Redirect back to dashboard if possible, or index
                window.location.href = 'dashboard.html?error=unauthorized';
                break;
            }
        }
    }
}

/**
 * Create toast container if it doesn't exist
 * @returns {HTMLElement}
 */
function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toastContainer';
    container.className = 'toast-container';
    document.body.appendChild(container);
    return container;
}

/**
 * Get icon for toast type
 * @param {string} type 
 * @returns {string}
 */
function getToastIcon(type) {
    const icons = {
        success: '✅',
        error: '❌',
        warning: '⚠️',
        info: 'ℹ️'
    };
    return icons[type] || icons.info;
}

/**
 * Show confirmation dialog
 * @param {string} message 
 * @returns {Promise<boolean>}
 */
async function confirm(message) {
    return window.confirm(message);
}

/**
 * Format date to readable string
 * @param {string} dateString 
 * @returns {string}
 */
function formatDate(dateString) {
    if (!dateString) return 'N/A';

    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}
/**
 * Format date string with timezone
 * @param {string} dateString 
 * @returns {string}
 */
function formatDateTime(dateString) {
    if (!dateString) return '-';

    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        timeZoneName: 'short'
    });
}
/**
 * Format relative time (e.g., "2 hours ago")
 * @param {string} dateString 
 * @returns {string}
 */
function formatRelativeTime(dateString) {
    if (!dateString) return 'N/A';

    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffSecs = Math.floor(diffMs / 1000);
    const diffMins = Math.floor(diffSecs / 60);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffSecs < 60) return 'Just now';
    if (diffMins < 60) return `${diffMins} minute${diffMins > 1 ? 's' : ''} ago`;
    if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
    if (diffDays < 30) return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
    return formatDate(dateString);
}

/**
 * Escape HTML to prevent XSS
 * @param {string} text 
 * @returns {string}
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Debounce function
 * @param {Function} func 
 * @param {number} wait 
 * @returns {Function}
 */
function debounce(func, wait = 300) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Validate email format
 * @param {string} email 
 * @returns {boolean}
 */
function isValidEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

/**
 * Validate username format
 * @param {string} username 
 * @returns {boolean}
 */
function isValidUsername(username) {
    // Alphanumeric and underscore, 3-20 characters
    const re = /^[a-zA-Z0-9_]{3,20}$/;
    return re.test(username);
}

/**
 * Validate password strength
 * @param {string} password 
 * @returns {{valid: boolean, message: string}}
 */
function validatePassword(password) {
    if (password.length < 8) {
        return { valid: false, message: 'Password must be at least 8 characters' };
    }
    if (!/[a-z]/.test(password)) {
        return { valid: false, message: 'Password must contain lowercase letter' };
    }
    if (!/[A-Z]/.test(password)) {
        return { valid: false, message: 'Password must contain uppercase letter' };
    }
    if (!/[0-9]/.test(password)) {
        return { valid: false, message: 'Password must contain number' };
    }
    return { valid: true, message: 'Password is strong' };
}

/**
 * Create modal dialog
 * @param {string} title 
 * @param {string} content 
 * @param {Array} buttons 
 * @returns {HTMLElement}
 */
function createModal(title, content, buttons = []) {
    // Remove existing modals
    document.querySelectorAll('.modal').forEach(m => m.remove());

    const modal = document.createElement('div');
    modal.className = 'modal active';

    const buttonsHtml = buttons.map(btn => `
        <button class="btn btn-${btn.type || 'secondary'}" onclick="${btn.onclick}">
            ${btn.label}
        </button>
    `).join('');

    modal.innerHTML = `
        <div class="modal-content">
            <div class="modal-header">
                <h3 class="modal-title">${title}</h3>
                <button class="modal-close" onclick="closeModal()">&times;</button>
            </div>
            <div class="modal-body">
                ${content}
            </div>
            <div class="modal-footer">
                ${buttonsHtml}
            </div>
        </div>
    `;

    document.body.appendChild(modal);

    // Close on background click
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            closeModal();
        }
    });

    return modal;
}

/**
 * Close modal
 */
function closeModal() {
    document.querySelectorAll('.modal').forEach(m => {
        m.classList.remove('active');
        setTimeout(() => m.remove(), 300);
    });
}

/**
 * Filter table rows
 * @param {string} tableId 
 * @param {string} searchValue 
 */
function filterTable(tableId, searchValue) {
    const table = document.getElementById(tableId);
    if (!table) return;

    const rows = table.querySelectorAll('tbody tr');
    const searchLower = searchValue.toLowerCase();

    rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        row.style.display = text.includes(searchLower) ? '' : 'none';
    });
}

/**
 * Sort table by column
 * @param {HTMLTableElement} table 
 * @param {number} columnIndex 
 * @param {boolean} ascending 
 */
function sortTable(table, columnIndex, ascending = true) {
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));

    rows.sort((a, b) => {
        const aText = a.cells[columnIndex].textContent.trim();
        const bText = b.cells[columnIndex].textContent.trim();

        // Try to parse as number
        const aNum = parseFloat(aText);
        const bNum = parseFloat(bText);

        if (!isNaN(aNum) && !isNaN(bNum)) {
            return ascending ? aNum - bNum : bNum - aNum;
        }

        // String comparison
        return ascending
            ? aText.localeCompare(bText)
            : bText.localeCompare(aText);
    });

    // Reappend rows in sorted order
    rows.forEach(row => tbody.appendChild(row));
}

/**
 * Copy text to clipboard
 * @param {string} text 
 */
async function copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
        showToast('Copied to clipboard', 'success');
    } catch (err) {
        showToast('Failed to copy', 'error');
    }
}

/**
 * Generate random ID
 * @returns {string}
 */
function generateId() {
    return Math.random().toString(36).substring(2, 15);
}

/**
 * Get query parameter from URL
 * @param {string} param 
 * @returns {string|null}
 */
function getQueryParam(param) {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get(param);
}

/**
 * Set query parameter in URL
 * @param {string} param 
 * @param {string} value 
 */
function setQueryParam(param, value) {
    const url = new URL(window.location);
    url.searchParams.set(param, value);
    window.history.pushState({}, '', url);
}

/**
 * Format file size
 * @param {number} bytes 
 * @returns {string}
 */
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';

    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));

    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

/**
 * Capitalize first letter
 * @param {string} str 
 * @returns {string}
 */
function capitalize(str) {
    if (!str) return '';
    return str.charAt(0).toUpperCase() + str.slice(1);
}

/**
 * Truncate text
 * @param {string} text 
 * @param {number} maxLength 
 * @returns {string}
 */
function truncate(text, maxLength = 50) {
    if (!text || text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
}

/**
 * Deep clone object
 * @param {object} obj 
 * @returns {object}
 */
function deepClone(obj) {
    return JSON.parse(JSON.stringify(obj));
}

/**
 * Check if object is empty
 * @param {object} obj 
 * @returns {boolean}
 */
function isEmpty(obj) {
    return Object.keys(obj).length === 0;
}

/**
 * Group array by key
 * @param {Array} array 
 * @param {string} key 
 * @returns {object}
 */
function groupBy(array, key) {
    return array.reduce((result, item) => {
        const group = item[key];
        if (!result[group]) {
            result[group] = [];
        }
        result[group].push(item);
        return result;
    }, {});
}

/**
 * Update application user display (Sidebar/Header)
 * @param {object} user 
 */
function updateAppUserDisplay(user) {
    if (!user) return;

    // Sidebar Name
    const nameEl = document.getElementById('userName');
    if (nameEl) {
        const fullName = [user.first_name, user.last_name].filter(Boolean).join(' ');
        nameEl.textContent = fullName || user.username;
    }

    // Sidebar Role
    const roleEl = document.getElementById('userRole');
    if (roleEl) {
        roleEl.textContent = (user.roles || []).join(', ') || user.user_role || 'User';
    }

    // Profile Avatar (First Letter)
    const avatarEl = document.getElementById('userAvatar');
    if (avatarEl) {
        // Use first name or username
        const source = user.first_name || user.username || 'U';
        avatarEl.textContent = source.charAt(0).toUpperCase();
    }
}