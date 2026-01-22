// Authentication Module
// Handles login, logout, session management, and route protection

// Session storage keys
const SESSION_KEY = 'rbac_session';
const TOKEN_KEY = 'rbac_token';
const REFRESH_TOKEN_KEY = 'bac_refresh_token';

// Cookie helper functions
function setCookie(name, value, expires) {
    let cookieString = `${name}=${encodeURIComponent(value)}; path=/`;
    if (expires) {
        cookieString += `; expires=${expires.toUTCString()}`;
    }
    document.cookie = cookieString;
}

function getCookie(name) {
    const nameEQ = name + "=";
    const ca = document.cookie.split(';');
    for (let i = 0; i < ca.length; i++) {
        let c = ca[i];
        while (c.charAt(0) === ' ') c = c.substring(1, c.length);
        if (c.indexOf(nameEQ) === 0) return decodeURIComponent(c.substring(nameEQ.length, c.length));
    }
    return null;
}

function deleteCookie(name) {
    document.cookie = `${name}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;`;
}

function getTokenExpiration(token) {
    try {
        const parts = token.split('.');
        if (parts.length !== 3) return null;
        const base64 = parts[1].replace(/-/g, '+').replace(/_/g, '/');
        const tokenData = JSON.parse(atob(base64));
        return tokenData.exp ? new Date(tokenData.exp * 1000) : null;
    } catch (error) {
        return null;
    }
}

/**
 * Login function
 * @param {string} username 
 * @param {string} password 
 * @returns {Promise<{success: boolean, message: string, user?: object}>}
 */
async function login(username, password) {
    try {
        const result = await apiLogin(username, password);

        if (result && result.access_token) {
            localStorage.setItem(TOKEN_KEY, result.access_token);
            setCookie(TOKEN_KEY, result.access_token, getTokenExpiration(result.access_token));
            if (result.refresh_token) {
                localStorage.setItem(REFRESH_TOKEN_KEY, result.refresh_token);
                setCookie(REFRESH_TOKEN_KEY, result.refresh_token, getTokenExpiration(result.refresh_token));
            }

            const user = await apiGetCurrentUser();

            const sessionData = {
                id: user.id,
                username: user.username,
                email: user.email,
                first_name: user.first_name,
                last_name: user.last_name,
                roles: [user.user_role], // Wrap single role in array for compatibility
                user_role: user.user_role,
                bank_id: user.bank_id,
                is_admin: user.user_role === 'admin',
                loginTime: new Date().toISOString()
            };

            localStorage.setItem(SESSION_KEY, JSON.stringify(sessionData));
            setCookie(SESSION_KEY, JSON.stringify(sessionData));

            return {
                success: true,
                message: 'Login successful',
                user: sessionData
            };
        }

        return {
            success: false,
            message: 'Invalid credentials'
        };
    } catch (error) {
        return {
            success: false,
            message: error.message || 'Login failed'
        };
    }
}

/**
 * Register new user
 * @param {object} userData 
 * @returns {Promise<{success: boolean, message: string, user?: object}>}
 */
async function register(userData) {
    try {
        await apiRegister(userData);
        // Auto-login after registration
        return await login(userData.username, userData.password);
    } catch (error) {
        return {
            success: false,
            message: error.message || 'Registration failed'
        };
    }
}

/**
 * Logout function with confirmation
 */
function logout() {
    const content = `<p>Are you sure you want to logout?</p>`;
    createModal('Confirm Logout', content, [
        { label: 'Cancel', type: 'secondary', onclick: 'closeModal()' },
        { label: 'Logout', type: 'danger', onclick: 'confirmLogout()' }
    ]);
}

function confirmLogout() {
    localStorage.removeItem(SESSION_KEY);
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
    deleteCookie(SESSION_KEY);
    deleteCookie(TOKEN_KEY);
    deleteCookie(REFRESH_TOKEN_KEY);
    window.location.href = 'index.html';
}

/**
 * Check if user is authenticated
 * @returns {boolean}
 */
function isAuthenticated() {
    const session = localStorage.getItem(SESSION_KEY) || getCookie(SESSION_KEY);
    const token = localStorage.getItem(TOKEN_KEY) || getCookie(TOKEN_KEY);

    if (!session || !token) {
        return false;
    }

    try {
        // Decode JWT payload
        const parts = token.split('.');
        if (parts.length !== 3) return false;

        // Base64Url to Base64
        const base64 = parts[1].replace(/-/g, '+').replace(/_/g, '/');
        const tokenData = JSON.parse(atob(base64));

        // Check if token is expired (exp is in seconds, Date.now() in ms)
        const currentTime = Math.floor(Date.now() / 1000);
        if (tokenData.exp && tokenData.exp < currentTime) {
            // Token expired
            localStorage.removeItem(SESSION_KEY);
            localStorage.removeItem(TOKEN_KEY);
            localStorage.removeItem(REFRESH_TOKEN_KEY);
            deleteCookie(SESSION_KEY);
            deleteCookie(TOKEN_KEY);
            deleteCookie(REFRESH_TOKEN_KEY);
            return false;
        }

        return true;
    } catch (error) {
        console.error('Auth verification error:', error);
        return false;
    }
}

/**
 * Get current logged in user
 * @returns {object|null}
 */
function getCurrentUser() {
    const session = localStorage.getItem(SESSION_KEY) || getCookie(SESSION_KEY);
    if (!session) return null;

    try {
        return JSON.parse(session);
    } catch (error) {
        return null;
    }
}

/**
 * Get authentication token
 * @returns {string|null}
 */
function getAuthToken() {
    return localStorage.getItem(TOKEN_KEY) || getCookie(TOKEN_KEY);
}

/**
 * Get refresh token
 * @returns {string|null}
 */
function getRefreshToken() {
    return localStorage.getItem(REFRESH_TOKEN_KEY) || getCookie(REFRESH_TOKEN_KEY);
}

/**
 * Refresh token orchestration
 * @returns {Promise<boolean>}
 */
async function refreshToken() {
    return await apiRefreshToken();
}

/**
 * Require authentication for page
 * Redirects to login if not authenticated
 */
function requireAuth() {
    if (!isAuthenticated()) {
        window.location.href = 'index.html';
    }
}

/**
 * Check if current user has specific role
 * @param {string} roleName 
 * @returns {boolean}
 */
function hasRole(roleName) {
    const user = getCurrentUser();
    if (!user) return false;

    return user.roles.includes(roleName);
}

/**
 * Check if current user has specific permission
 * @param {string} permission 
 * @returns {boolean}
 */
function hasPermission(permission) {
    const user = getCurrentUser();
    if (!user) return false;

    // Admin users have all permissions
    if (user.is_admin) return true;

    // Check if any of user's roles have the permission
    return user.roles.some(roleName => {
        const role = getRoleByName(roleName);
        return role && role.permissions.includes(permission);
    });
}

/**
 * Check if current user is admin
 * @returns {boolean}
 */
function isAdmin() {
    const user = getCurrentUser();
    return user && user.is_admin;
}

/**
 * Update user session (after profile changes)
 * @param {object} userData 
 */
function updateSession(userData) {
    const currentSession = getCurrentUser();
    if (!currentSession) return;

    const updatedSession = {
        ...currentSession,
        ...userData
    };

    localStorage.setItem(SESSION_KEY, JSON.stringify(updatedSession));
    setCookie(SESSION_KEY, JSON.stringify(updatedSession));
}

/**
 * Refresh session from user data
 * @param {string} username 
 */
function refreshSession(username) {
    const user = findUserByUsername(username);
    if (!user) return;

    const sessionData = {
        id: user.id,
        username: user.username,
        email: user.email,
        full_name: user.full_name,
        roles: user.roles,
        is_admin: user.is_admin,
        attributes: user.attributes,
        loginTime: getCurrentUser()?.loginTime || new Date().toISOString()
    };

    localStorage.setItem(SESSION_KEY, JSON.stringify(sessionData));
    setCookie(SESSION_KEY, JSON.stringify(sessionData));
}