// API Integration Module
// This file handles all API communication with the FastAPI backend
// Currently uses mock data, but ready for real API integration

// API Configuration
const API_CONFIG = {
    baseURL: '/api/v1',
    timeout: 30000,
    headers: {
        'Content-Type': 'application/json'
    }
};

/**
 * Make API request
 * @param {string} endpoint 
 * @param {object} options 
 * @returns {Promise<any>}
 */
async function apiRequest(endpoint, options = {}) {
    const url = `${API_CONFIG.baseURL}${endpoint}`;

    const config = {
        method: options.method || 'GET',
        headers: {
            ...API_CONFIG.headers,
            ...options.headers
        },
        ...options
    };

    // Add auth token if available (from auth.js)
    if (typeof getAuthToken === 'function') {
        const token = getAuthToken();
        if (token) {
            config.headers['Authorization'] = `Bearer ${token}`;
        }
    }

    // Add body if present
    if (options.body) {
        if (options.body instanceof URLSearchParams) {
            config.body = options.body;
            // Fetch will handle Content-Type for URLSearchParams automatically,
            // but we can be explicit or let our default be overridden.
            if (config.headers['Content-Type'] === 'application/json') {
                delete config.headers['Content-Type'];
            }
        } else {
            config.body = JSON.stringify(options.body);
        }
    }

    try {
        const response = await fetch(url, config);

        if (!response.ok) {
            const error = await response.json().catch(() => ({ detail: 'API request failed' }));
            throw new Error(error.detail || 'API request failed');
        }

        const json = await response.json();
        // Handle custom response wrapper { success, message, data }
        if (json && typeof json === 'object' && json.hasOwnProperty('data') && json.hasOwnProperty('success')) {
            return json.data;
        }
        return json;
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

/**
 * API Endpoints - Ready for backend integration
 */

// ============ Authentication Endpoints ============

/**
 * Login to the system
 * Backend endpoint: POST /auth/login
 * @param {string} username 
 * @param {string} password 
 * @returns {Promise<{access_token: string, token_type: string}>}
 */
async function apiLogin(username, password) {
    // Build form data for OAuth2 login which many FastAPI apps use
    // But let's check if the backend uses JSON or Form data.
    // Usually /auth/login uses Form data for OAuth2PasswordRequestForm

    // OAuth2PasswordRequestForm expects application/x-www-form-urlencoded
    const params = new URLSearchParams();
    params.append('username', username);
    params.append('password', password);

    return await apiRequest('/auth/login', {
        method: 'POST',
        body: params
    });
}

/**
 * Register new user
 * Backend endpoint: POST /auth/register
 * @param {object} userData 
 * @returns {Promise<object>}
 */
async function apiRegister(userData) {
    return await apiRequest('/auth/register', {
        method: 'POST',
        body: userData
    });
}

/**
 * Get current user info
 * Backend endpoint: GET /auth/me
 * @returns {Promise<object>}
 */
async function apiGetCurrentUser() {
    return await apiRequest('/users/me');
}

// ============ RBAC Endpoints ============

/**
 * Get all users
 * Backend endpoint: GET /rbac/users
 * @returns {Promise<Array>}
 */
async function apiGetUsers() {
    return await apiRequest('/users'); // Backend uses /users for general user listing
}

/**
 * Get user by ID
 * Backend endpoint: GET /rbac/users/{user_id}
 * @param {number} userId 
 * @returns {Promise<object>}
 */
async function apiGetUser(userId) {
    return await apiRequest(`/users/${userId}`);
}

/**
 * Create new user
 * Backend endpoint: POST /rbac/users
 * @param {object} userData 
 * @returns {Promise<object>}
 */
async function apiCreateUser(userData) {
    return await apiRequest('/users', {
        method: 'POST',
        body: userData
    });
}

/**
 * Update user
 * Backend endpoint: PUT /rbac/users/{user_id}
 * @param {number} userId 
 * @param {object} userData 
 * @returns {Promise<object>}
 */
async function apiUpdateUser(userId, userData) {
    return await apiRequest(`/users/${userId}`, {
        method: 'PUT',
        body: userData
    });
}

/**
 * Delete user
 * Backend endpoint: DELETE /rbac/users/{user_id}
 * @param {number} userId 
 * @returns {Promise<{success: boolean}>}
 */
async function apiDeleteUser(userId) {
    return await apiRequest(`/users/${userId}`, {
        method: 'DELETE'
    });
}

/**
 * Get all roles
 * Backend endpoint: GET /rbac/roles
 * @returns {Promise<Array>}
 */
async function apiGetRoles() {
    return await apiRequest('/rbac');
}

/**
 * Create new role
 * Backend endpoint: POST /rbac/roles
 * @param {object} roleData 
 * @returns {Promise<object>}
 */
async function apiCreateRole(roleData) {
    return await apiRequest('/rbac', {
        method: 'POST',
        body: roleData
    });
}

/**
 * Assign role to user
 * Backend endpoint: POST /rbac/roles/assign
 * @param {string} username 
 * @param {string} roleName 
 * @returns {Promise<{success: boolean}>}
 */
async function apiAssignRole(username, roleName) {
    return await apiRequest('/rbac/assign', {
        method: 'POST',
        body: { username, role: roleName }
    });
}

/**
 * Remove role from user
 * Backend endpoint: DELETE /rbac/roles/revoke
 * @param {string} username 
 * @param {string} roleName 
 * @returns {Promise<{success: boolean}>}
 */
async function apiRevokeRole(username, roleName) {
    return await apiRequest('/rbac/revoke', {
        method: 'DELETE',
        body: { username, role: roleName }
    });
}

/**
 * Check permission
 * Backend endpoint: POST /rbac/check-permission
 * @param {string} username 
 * @param {string} resource 
 * @param {string} action 
 * @returns {Promise<{allowed: boolean}>}
 */
async function apiCheckPermission(username, resource, action) {
    return await apiRequest('/authorization/check', {
        method: 'POST',
        body: { username, resource, action }
    });
}

// ============ ABAC Endpoints ============

/**
 * Get all ABAC policies
 * Backend endpoint: GET /abac/policies
 * @returns {Promise<Array>}
 */
async function apiGetPolicies() {
    return await apiRequest('/abac/policies');
}

/**
 * Create ABAC policy
 * Backend endpoint: POST /abac/policies
 * @param {object} policyData 
 * @returns {Promise<object>}
 */
async function apiCreatePolicy(policyData) {
    return await apiRequest('/abac/policies', {
        method: 'POST',
        body: policyData
    });
}

/**
 * Test ABAC policy
 * Backend endpoint: POST /abac/test
 * @param {object} userAttributes 
 * @param {object} resourceAttributes 
 * @param {number} policyId 
 * @returns {Promise<{allowed: boolean, policy: object}>}
 */
async function apiTestPolicy(userAttributes, resourceAttributes, policyId) {
    return await apiRequest('/abac/test', {
        method: 'POST',
        body: {
            user_attributes: userAttributes,
            resource_attributes: resourceAttributes,
            policy_id: policyId
        }
    });
}

// ============ ReBAC Endpoints ============

/**
 * Get all relationships
 * Backend endpoint: GET /rebac/relationships
 * @returns {Promise<Array>}
 */
async function apiGetRelationships() {
    return await apiRequest('/rebac/relationships');
}

/**
 * Create relationship
 * Backend endpoint: POST /rebac/relationships
 * @param {object} relationshipData 
 * @returns {Promise<object>}
 */
async function apiCreateRelationship(relationshipData) {
    return await apiRequest('/rebac/relationships', {
        method: 'POST',
        body: relationshipData
    });
}

/**
 * Delete relationship
 * Backend endpoint: DELETE /rebac/relationships/{relationship_id}
 * @param {number} relationshipId 
 * @returns {Promise<{success: boolean}>}
 */
async function apiDeleteRelationship(relationshipId) {
    return await apiRequest(`/rebac/relationships/${relationshipId}`, {
        method: 'DELETE'
    });
}

/**
 * Check relationship path
 * Backend endpoint: POST /rebac/check-path
 * @param {string} sourceId 
 * @param {string} targetId 
 * @returns {Promise<{has_path: boolean, path: Array}>}
 */
async function apiCheckPath(sourceId, targetId) {
    // TODO: Replace mock with real API call
    // return await apiRequest('/rebac/check-path', {
    //     method: 'POST',
    //     body: { source_id: sourceId, target_id: targetId }
    // });

    // Mock implementation
    const path = findRelationshipPath(sourceId, targetId);
    return {
        has_path: path !== null,
        path: path || []
    };
}