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
            let errorPayload = null;
            try {
                const errText = await response.text();
                errorPayload = errText ? JSON.parse(errText) : null;
            } catch (_) {
                errorPayload = null;
            }

            // Handle 403 Forbidden
            if (response.status === 403) {
                console.warn('Access Denied (403):', errorPayload);
                const errorMessage = (errorPayload && (errorPayload.detail || errorPayload.message)) || 'You are not authorized to perform this action.';

                // Show friendly message if UI utility is available
                if (typeof showAccessDeniedMessage === 'function') {
                    showAccessDeniedMessage(errorMessage);
                } else {
                    alert('Access Denied: ' + errorMessage);
                }

                throw new Error('ACCESS_DENIED');
            }

            const errorMessage = (errorPayload && (errorPayload.detail || errorPayload.message)) || `HTTP ${response.status}: ${response.statusText}`;
            console.error('API Error Response:', errorPayload || response.statusText);
            throw new Error(errorMessage);
        }

        // Some endpoints may return 204 or empty body; avoid JSON parse errors
        const rawText = await response.text();
        if (!rawText) return {};
        let json;
        try {
            json = JSON.parse(rawText);
        } catch (e) {
            console.error('API JSON parse error:', e, rawText);
            throw new Error('Unexpected response format');
        }
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
 * Update current user profile
 * @param {object} profileData 
 * @returns {Promise<object>}
 */
async function apiUpdateProfile(profileData) {
    return await apiRequest('/users/me', {
        method: 'PATCH',
        body: profileData
    });
}

/**
 * Change current user password
 * @param {object} passwordData {current_password, new_password}
 * @returns {Promise<object>}
 */
async function apiChangePassword(passwordData) {
    return await apiRequest('/users/me/password', {
        method: 'POST',
        body: passwordData
    });
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
    const payload = { ...userData };
    // backend expects user_role, not role
    if (payload.role && !payload.user_role) {
        payload.user_role = payload.role;
        delete payload.role;
    }
    return await apiRequest('/users/', {
        method: 'POST',
        body: payload
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
    const payload = { ...userData };
    if (payload.role && !payload.user_role) {
        payload.user_role = payload.role;
        delete payload.role;
    }
    return await apiRequest(`/users/${userId}`, {
        method: 'PUT',
        body: payload
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
 * Get audit trail for a user
 * Backend endpoint: GET /audit-trail/users/{user_id}
 * @param {number} userId 
 * @param {number} skip - Number of records to skip (default: 0)
 * @param {number} limit - Maximum number of records to return (default: 100)
 * @returns {Promise<{total: number, logs: Array}>}
 */
async function apiGetUserAuditTrail(userId, skip = 0, limit = 100) {
    return await apiRequest(`/audit-trail/users/${userId}?skip=${skip}&limit=${limit}`, {
        method: 'GET'
    });
}

/**
 * Get audit trail for all user entity logs
 * Backend endpoint: GET /audit-trail/users
 * @param {number} skip - Number of records to skip (default: 0)
 * @param {number} limit - Maximum number of records to return (default: 100)
 * @returns {Promise<Array>}
 */
async function apiGetUsersAuditTrail(skip = 0, limit = 100) {
    return await apiRequest(`/audit-trail/users?skip=${skip}&limit=${limit}`, {
        method: 'GET'
    });
}

/**
 * Get all audit logs
 * Backend endpoint: GET /audit-trail/
 * @param {number} skip - Number of records to skip (default: 0)
 * @param {number} limit - Maximum number of records to return (default: 100)
 * @returns {Promise<Array>}
 */
async function apiGetAllAuditLogs(skip = 0, limit = 100, resourceType = null) {
    const resourceParam = resourceType ? `&resource_type=${encodeURIComponent(resourceType)}` : '';
    return await apiRequest(`/audit-trail/?skip=${skip}&limit=${limit}${resourceParam}`, {
        method: 'GET'
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
 * Update role
 * Backend endpoint: PUT /roles/{id}
 * @param {number} roleId 
 * @param {object} roleData 
 * @returns {Promise<object>}
 */
async function apiUpdateRole(roleId, roleData) {
    return await apiRequest(`/roles/${roleId}`, {
        method: 'PUT',
        body: roleData
    });
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

/**
 * Get all effective permissions for current user
 * @returns {Promise<object>}
 */
async function apiGetUserPermissions() {
    return await apiRequest('/authorization/permissions');
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
 * Update ABAC policy
 * Backend endpoint: PUT /abac/policies/{policy_id}
 * @param {number} policyId 
 * @param {object} policyData 
 * @returns {Promise<object>}
 */
async function apiUpdatePolicy(policyId, policyData) {
    return await apiRequest(`/abac/policies/${policyId}`, {
        method: 'PUT',
        body: policyData
    });
}

/**
 * Delete ABAC policy
 * Backend endpoint: DELETE /abac/policies/{policy_id}
 * @param {number} policyId 
 * @returns {Promise<void>}
 */
async function apiDeletePolicy(policyId) {
    return await apiRequest(`/abac/policies/${policyId}`, {
        method: 'DELETE'
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
 * Update relationship
 * Backend endpoint: PUT /rebac/relationships/{relationship_id}
 * @param {number} relationshipId 
 * @param {object} relationshipData 
 * @returns {Promise<object>}
 */
async function apiUpdateRelationship(relationshipId, relationshipData) {
    return await apiRequest(`/rebac/relationships/${relationshipId}`, {
        method: 'PUT',
        body: relationshipData
    });
}

/**
 * Get ABAC Policy Stats
 * Backend endpoint: GET /abac/stats
 * @returns {Promise<{total_policies: number, applied_policies: number}>}
 */
async function apiGetAbacStats() {
    return await apiRequest('/abac/stats');
}

/**
 * Get available ABAC attributes metadata
 * Backend endpoint: GET /abac/metadata/attributes
 * Returns comprehensive metadata including:
 * - attribute_groups: Grouped attributes with operators and value sources
 * - global_operators: All available operators
 * @returns {Promise<object>}
 */
async function apiGetAbacAttributes() {
    return await apiRequest('/abac/metadata/attributes');
}

// ============ Lookup Table Endpoints ============

/**
 * Get all departments
 * Backend endpoint: GET /lookups/departments
 * @param {boolean} activeOnly - Filter for active departments only (default: true)
 * @returns {Promise<Array>}
 */
async function apiGetDepartments(activeOnly = true) {
    return await apiRequest(`/lookups/departments?active_only=${activeOnly}`);
}

/**
 * Create a new department
 * Backend endpoint: POST /lookups/departments
 * @param {object} data - Department data {name, code, description, is_active, display_order}
 * @returns {Promise<object>}
 */
async function apiCreateDepartment(data) {
    return await apiRequest('/lookups/departments', {
        method: 'POST',
        body: data
    });
}

/**
 * Update a department
 * Backend endpoint: PUT /lookups/departments/{id}
 * @param {number} id - Department ID
 * @param {object} data - Updated department data
 * @returns {Promise<object>}
 */
async function apiUpdateDepartment(id, data) {
    return await apiRequest(`/lookups/departments/${id}`, {
        method: 'PUT',
        body: data
    });
}

/**
 * Delete a department
 * Backend endpoint: DELETE /lookups/departments/{id}
 * @param {number} id - Department ID
 * @returns {Promise<void>}
 */
async function apiDeleteDepartment(id) {
    return await apiRequest(`/lookups/departments/${id}`, {
        method: 'DELETE'
    });
}

/**
 * Get all locations
 * Backend endpoint: GET /lookups/locations
 * @param {boolean} activeOnly - Filter for active locations only (default: true)
 * @param {string} region - Optional region filter
 * @returns {Promise<Array>}
 */
async function apiGetLocations(activeOnly = true, region = null) {
    let url = `/lookups/locations?active_only=${activeOnly}`;
    if (region) {
        url += `&region=${encodeURIComponent(region)}`;
    }
    return await apiRequest(url);
}

/**
 * Create a new location
 * Backend endpoint: POST /lookups/locations
 * @param {object} data - Location data {name, code, description, region, is_active, display_order}
 * @returns {Promise<object>}
 */
async function apiCreateLocation(data) {
    return await apiRequest('/lookups/locations', {
        method: 'POST',
        body: data
    });
}

/**
 * Update a location
 * Backend endpoint: PUT /lookups/locations/{id}
 * @param {number} id - Location ID
 * @param {object} data - Updated location data
 * @returns {Promise<object>}
 */
async function apiUpdateLocation(id, data) {
    return await apiRequest(`/lookups/locations/${id}`, {
        method: 'PUT',
        body: data
    });
}

/**
 * Delete a location
 * Backend endpoint: DELETE /lookups/locations/{id}
 * @param {number} id - Location ID
 * @returns {Promise<void>}
 */
async function apiDeleteLocation(id) {
    return await apiRequest(`/lookups/locations/${id}`, {
        method: 'DELETE'
    });
}

/**
 * Get ReBAC options for dropdowns
 * Backend endpoint: GET /rebac/metadata/options
 * @returns {Promise<object>}
 */
async function apiGetRebacOptions() {
    return await apiRequest('/rebac/metadata/options');
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
    if (bankId) {
        return await apiRequest(`/templates/bank/${bankId}`);
    }
    return await apiRequest('/templates/');
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
        data_json: submissionData.submission_data || submissionData.data_json,
        fieldman_id: submissionData.username || submissionData.fieldman_id
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
async function apiGetSubmissions(page = 1, pageSize = 10, filters = {}) {
    let url = `/submissions/?page=${page}&page_size=${pageSize}`;
    if (filters.status) url += `&status=${encodeURIComponent(filters.status)}`;
    if (filters.template_id) url += `&template_id=${encodeURIComponent(filters.template_id)}`;
    if (filters.bank_id) url += `&bank_id=${encodeURIComponent(filters.bank_id)}`;
    if (filters.search) url += `&search=${encodeURIComponent(filters.search)}`;
    return await apiRequest(url);
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