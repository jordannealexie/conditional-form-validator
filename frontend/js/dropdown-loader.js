/**
 * Dropdown Loader Module
 * ========================
 * SINGLE SOURCE OF TRUTH for all form dropdowns across the application.
 * 
 * This module provides centralized dropdown loading from the backend.
 * All pages (Register, User Management, Profile) MUST use this module.
 * 
 * NO HARDCODING - All values come from the backend /api/v1/metadata endpoints.
 * 
 * Usage:
 *   // Load all dropdown data (call once on page load)
 *   await DropdownLoader.loadAll();
 *   
 *   // Build dropdown options HTML
 *   const roleOptions = DropdownLoader.buildOptions('roles', selectedValue);
 *   const deptOptions = DropdownLoader.buildOptions('departments', selectedValue);
 *   const locOptions = DropdownLoader.buildOptions('locations', selectedValue);
 *   const levelOptions = DropdownLoader.buildOptions('levels', selectedValue);
 *   
 *   // Populate a select element directly
 *   DropdownLoader.populateSelect('mySelectId', 'departments', selectedValue);
 */

const DropdownLoader = (function() {
    'use strict';

    // ============ Private State ============
    
    // Cached dropdown data from backend
    let _cache = {
        roles: null,
        departments: null,
        locations: null,
        levels: null,
        _loaded: false,
        _loading: null // Promise to prevent multiple simultaneous loads
    };

    // API endpoint for form metadata
    const METADATA_ENDPOINT = 'http://localhost:8000/api/v1/metadata/form-dropdowns';

    // ============ Private Methods ============

    /**
     * Make API request to fetch dropdown metadata
     */
    async function _fetchMetadata() {
        const url = METADATA_ENDPOINT;
        const config = {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        };

        // Add auth token if available (for authenticated pages)
        if (typeof getAuthToken === 'function') {
            const token = getAuthToken();
            if (token) {
                config.headers['Authorization'] = `Bearer ${token}`;
            }
        }

        try {
            const response = await fetch(url, config);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            const json = await response.json();
            // Handle wrapped response format { data: { ... } }
            return json.data || json;
        } catch (error) {
            console.error('DropdownLoader: Failed to fetch metadata:', error);
            throw error;
        }
    }

    /**
     * Escape HTML to prevent XSS
     */
    function _escapeHtml(text) {
        if (typeof escapeHtml === 'function') {
            return escapeHtml(text);
        }
        const div = document.createElement('div');
        div.textContent = text || '';
        return div.innerHTML;
    }

    // ============ Public API ============

    return {
        /**
         * Load all dropdown data from backend
         * Call this once on page load before using any dropdowns.
         * 
         * @returns {Promise<Object>} The loaded dropdown data
         */
        async loadAll() {
            console.log('[DropdownLoader] loadAll() called');
            // Return cached data if already loaded
            if (_cache._loaded) {
                return {
                    roles: _cache.roles,
                    departments: _cache.departments,
                    locations: _cache.locations,
                    levels: _cache.levels
                };
            }

            // Prevent multiple simultaneous loads
            if (_cache._loading) {
                return _cache._loading;
            }

            _cache._loading = (async () => {
                try {
                    const data = await _fetchMetadata();
                    
                    _cache.roles = Array.isArray(data.roles) ? data.roles : [];
                    _cache.departments = Array.isArray(data.departments) ? data.departments : [];
                    _cache.locations = Array.isArray(data.locations) ? data.locations : [];
                    _cache.levels = Array.isArray(data.levels) ? data.levels : [];
                    _cache._loaded = true;

                    console.log('DropdownLoader: Loaded metadata -', {
                        roles: _cache.roles.length,
                        departments: _cache.departments.length,
                        locations: _cache.locations.length,
                        levels: _cache.levels.length
                    });

                    return {
                        roles: _cache.roles,
                        departments: _cache.departments,
                        locations: _cache.locations,
                        levels: _cache.levels
                    };
                } catch (error) {
                    console.error('DropdownLoader: Error loading metadata:', error);
                    // Set empty arrays on error
                    _cache.roles = [];
                    _cache.departments = [];
                    _cache.locations = [];
                    _cache.levels = [];
                    _cache._loaded = false;
                    throw error;
                } finally {
                    _cache._loading = null;
                }
            })();

            return _cache._loading;
        },

        /**
         * Build HTML options string for a dropdown
         * 
         * @param {string} type - 'roles', 'departments', 'locations', or 'levels'
         * @param {string|number} [selectedValue] - Currently selected value
         * @param {Object} [options] - Additional options
         * @param {boolean} [options.includeEmpty=true] - Include empty "Select..." option
         * @param {string} [options.emptyLabel] - Custom label for empty option
         * @returns {string} HTML options string
         */
        buildOptions(type, selectedValue = '', options = {}) {
            const includeEmpty = options.includeEmpty !== false;
            const emptyLabel = options.emptyLabel || `Select ${type.slice(0, -1)}`;
            
            const items = _cache[type] || [];
            let html = '';

            if (includeEmpty) {
                html += `<option value="">${_escapeHtml(emptyLabel)}</option>`;
            }

            items.forEach(item => {
                // Handle both { value, label } and { name } formats
                const value = item.value !== undefined ? item.value : item.name;
                const label = item.label || item.name || value;
                const selected = String(value) === String(selectedValue) ? 'selected' : '';
                const title = item.description ? `title="${_escapeHtml(item.description)}"` : '';
                
                html += `<option value="${_escapeHtml(String(value))}" ${selected} ${title}>${_escapeHtml(label)}</option>`;
            });

            return html;
        },

        /**
         * Populate a select element with dropdown options
         * 
         * @param {string|HTMLElement} selectElement - Element ID or element reference
         * @param {string} type - 'roles', 'departments', 'locations', or 'levels'
         * @param {string|number} [selectedValue] - Currently selected value
         * @param {Object} [options] - Additional options passed to buildOptions
         */
        populateSelect(selectElement, type, selectedValue = '', options = {}) {
            const select = typeof selectElement === 'string' 
                ? document.getElementById(selectElement) 
                : selectElement;
            
            if (!select) {
                console.warn(`[DropdownLoader] Select element not found: ${selectElement}`);
                return;
            }

            const html = this.buildOptions(type, selectedValue, options);
            console.log(`[DropdownLoader] Populating ${selectElement} with ${type}: ${(_cache[type] || []).length} options`);
            select.innerHTML = html;
        },

        /**
         * Get raw dropdown data
         * 
         * @param {string} type - 'roles', 'departments', 'locations', or 'levels'
         * @returns {Array} Array of dropdown items
         */
        getData(type) {
            return _cache[type] || [];
        },

        /**
         * Check if data is loaded
         * @returns {boolean}
         */
        isLoaded() {
            return _cache._loaded;
        },

        /**
         * Force reload of dropdown data
         * Use this after admin changes to roles/departments/locations
         * 
         * @returns {Promise<Object>}
         */
        async reload() {
            _cache._loaded = false;
            _cache._loading = null;
            return this.loadAll();
        },

        /**
         * Get specific dropdown items as value/label pairs
         * Useful for custom dropdown implementations
         * 
         * @param {string} type - 'roles', 'departments', 'locations', or 'levels'
         * @returns {Array<{value: string, label: string}>}
         */
        getOptions(type) {
            const items = _cache[type] || [];
            return items.map(item => ({
                value: item.value !== undefined ? item.value : item.name,
                label: item.label || item.name || item.value,
                description: item.description
            }));
        }
    };
})();

// Make available globally
if (typeof window !== 'undefined') {
    window.DropdownLoader = DropdownLoader;
}
