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

        if (response.status === 401 && !options._retry && typeof refreshToken === 'function') {
            options._retry = true;
            try {
                const refreshed = await refreshToken();
                if (refreshed) {
                    // Retry original request with new token
                    const newToken = getAuthToken();
                    config.headers['Authorization'] = `Bearer ${newToken}`;
                    const retryResponse = await fetch(url, config);
                    const retryJson = await retryResponse.json();
                    if (retryJson && typeof retryJson === 'object' && retryJson.hasOwnProperty('data')) {
                        return retryJson.data;
                    }
                    return retryJson;
                }
            } catch (err) {
                console.error('Refresh token failed:', err);
            }
        }

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
    return await apiRequest('/auth/me');
}

/**
 * Refresh access token
 * @returns {Promise<boolean>}
 */
async function apiRefreshToken() {
    const refreshTokenValue = getRefreshToken();
    if (!refreshTokenValue) return false;

    try {
        const response = await fetch(`${API_CONFIG.baseURL}/auth/refresh`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ refresh_token: refreshTokenValue })
        });

        if (!response.ok) return false;

        const json = await response.json();
        const data = json.data || json;

        if (data && data.access_token) {
            localStorage.setItem('rbac_token', data.access_token);
            return true;
        }
        return false;
    } catch (err) {
        return false;
    }
}

// ============ RBAC Endpoints ============

/**
 * Get all users
 * Backend endpoint: GET /rbac/users
 * @returns {Promise<Array>}
 */
async function apiGetUsers() {
    return await apiRequest('/users/'); // Backend uses /users for general user listing
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
    return await apiRequest('/users/', {
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
 * Get all roles with permissions
 * Backend endpoint: GET /roles
 * @returns {Promise<Array>}
 */
async function apiGetRoles() {
    return await apiRequest('/roles/');
}

/**
 * Create new role
 * Backend endpoint: POST /roles
 * @param {object} roleData { name, description?, permissions? }
 * @returns {Promise<object>}
 */
async function apiCreateRole(roleData) {
    return await apiRequest('/roles/', {
        method: 'POST',
        body: roleData
    });
}

/**
 * Delete role
 * Backend endpoint: DELETE /roles/{id}
 * @param {number} roleId 
 * @returns {Promise<object>}
 */
async function apiDeleteRole(roleId) {
    return await apiRequest(`/roles/${roleId}`, { method: 'DELETE' });
}

/**
 * Get role permissions
 * Backend endpoint: GET /roles/{id}/permissions
 * @param {number} roleId 
 * @returns {Promise<object>}
 */
async function apiGetRolePermissions(roleId) {
    return await apiRequest(`/roles/${roleId}/permissions`);
}

/**
 * Assign role to user
 * Backend endpoint: POST /rbac/roles/assign
 * @param {string} username 
 * @param {string} roleName 
 * @returns {Promise<{success: boolean}>}
 */
async function apiAssignRole(username, roleName) {
    return await apiRequest('/rbac/roles/assign', {
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
    return await apiRequest('/rbac/roles/revoke', {
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
    return await apiRequest('/abac/check', {
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

// ============ Form System Endpoints ============

/**
 * Get all available banks
 * @returns {Promise<Array>}
 */
async function apiGetBanks() {
    return await apiRequest('/banks/');
}

/**
 * Get templates for a bank
 * @param {number} bankId 
 * @returns {Promise<Array>}
 */
async function apiGetTemplates(bankId) {
    return await apiRequest(`/templates/bank/${bankId}`);
}

/**
 * Get single template by ID
 * @param {number} templateId 
 * @returns {Promise<object>}
 */
async function apiGetTemplate(templateId) {
    return await apiRequest(`/templates/${templateId}`);
}

/**
 * Create a new form submission
 * @param {object} submissionData 
 * @returns {Promise<object>}
 */
async function apiSubmitForm(submissionData) {
    // submissionData should already contain template_id, status, and data_json
    // But for backward compatibility with frontend code that might pass old format:
    const payload = {
        template_id: submissionData.template_id,
        status: submissionData.status || 'draft',
        data_json: submissionData.submission_data || submissionData.data_json
    };

    return await apiRequest('/submissions/', {
        method: 'POST',
        body: payload
    });
}

/**
 * Get all submissions (paginated)
 * @param {number} page 
 * @param {number} pageSize 
 * @returns {Promise<object>}
 */
async function apiGetSubmissions(page = 1, pageSize = 10) {
    return await apiRequest(`/submissions/?page=${page}&page_size=${pageSize}`);
}

/**
 * Validate a submission without saving
 * @param {number} templateId 
 * @param {object} submissionData 
 * @returns {Promise<object>}
 */
async function apiValidateSubmission(templateId, submissionData) {
    return await apiRequest('/submissions/validate', {
        method: 'POST',
        body: { template_id: templateId, submission_data: submissionData }
    });
}


/**
 * Get single submission details
 * @param {number} submissionId 
 * @returns {Promise<object>}
 */
async function apiGetSubmission(submissionId) {
    return await apiRequest(`/submissions/${submissionId}`);
}

/**
 * Update submission (draft only)
 * @param {number} submissionId 
 * @param {object} data { data_json?, status? }
 * @returns {Promise<object>}
 */
async function apiUpdateSubmission(submissionId, data) {
    return await apiRequest(`/submissions/${submissionId}`, { method: 'PUT', body: data });
}

/**
 * Delete submission (own draft only)
 * @param {number} submissionId 
 * @returns {Promise<object>}
 */
async function apiDeleteSubmission(submissionId) {
    return await apiRequest(`/submissions/${submissionId}`, { method: 'DELETE' });
}

/**
 * Review submission (supervisor): approve or reject
 * @param {number} submissionId 
 * @param {object} data { action: 'approve'|'reject', comment? }
 * @returns {Promise<object>}
 */
async function apiReviewSubmission(submissionId, data) {
    return await apiRequest(`/submissions/${submissionId}/review`, { method: 'POST', body: data });
}

/**
 * Upload file for form. Returns { token, field_id, original_filename, ... }.
 * @param {FormData} formData with 'file', 'field_id', optionally 'submission_id'
 * @returns {Promise<object>}
 */
async function apiUploadFile(formData) {
    const url = `${API_CONFIG.baseURL}/files/upload`;
    const headers = {};
    if (typeof getAuthToken === 'function') {
        const t = getAuthToken();
        if (t) headers['Authorization'] = `Bearer ${t}`;
    }
    const r = await fetch(url, { method: 'POST', body: formData, headers });
    const j = await r.json();
    if (!r.ok) throw new Error(j.detail || j.message || 'Upload failed');
    return (j && j.data) ? j.data : j;
}

/**
 * Get file download URL by token (for use in href or iframe).
 * The actual download requires auth; this returns the API path.
 * @param {string} token 
 * @returns {string}
 */
function apiGetFileUrl(token) {
    return `${API_CONFIG.baseURL}/files/${token}`;
}