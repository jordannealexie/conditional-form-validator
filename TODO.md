# Conditional Form Validator Backend - Implementation Plan

## Phase 1: Backend Core Fixes
- [x] 1.1 Update JWT token expiry (15 min access, 7 day refresh)
- [ ] 1.2 Create audit_logs table and integration
- [x] 1.3 Fix database schema column names to match spec
- [x] 1.4 Update FormTemplate model (form_type kept, name added)
- [x] 1.5 Update FormFile model (field_id confirmed)
- [x] 1.6 Add reviewed_comment column to FormSubmission

## Phase 2: Complete Bank Templates
- [x] 2.1 Create BDO Credit Card Application template (16 fields)
- [x] 2.2 Create Maya Personal Loan template (15 fields)
- [x] 2.3 Create Security Bank KYC template (16 fields)
- [x] 2.4 Add conditional logic with show_if (all/any/not operators)
- [x] 2.5 Add file upload fields with token validation

## Phase 3: Frontend UI/UX Consistency
- [x] 3.1 Fix Profile page CSS (add missing card-header/card-body styles)
- [x] 3.2 Remove inline styles from profile page
- [x] 3.3 Standardize activity table styling
- [x] 3.4 Add missing CSS components to index.css
- [x] 3.5 Ensure all pages use consistent spacing and typography
- [x] 3.6 Update FormRenderer.js with proper CSS classes
- [x] 3.7 Update form-fill.html to use design system

## Phase 4: Documentation & Testing
- [ ] 4.1 Update README with API documentation
- [ ] 4.2 Document JSONSchema validation patterns
- [ ] 4.3 Test all API endpoints
- [ ] 4.4 Test frontend authentication flow

---

## Progress Summary (Completed)

### Backend Changes
1. **JWT Configuration** (`backend/app/core/config.py`)
   - ACCESS_TOKEN_EXPIRE_MINUTES: 15 (was 192 hours)
   - Added REFRESH_TOKEN_EXPIRE_DAYS: 7

2. **Auth Endpoint** (`backend/app/api/v1/endpoints/auth.py`)
   - Updated refresh token expiry to use settings.REFRESH_TOKEN_EXPIRE_DAYS

3. **Form Models** (`backend/app/models/forms.py`)
   - Added `form_type` column to FormTemplate (optional category)
   - Confirmed `field_id` column in FormFile
   - Added description for `reviewed_comment` in FormSubmission

### Bank Templates (backend/scripts/seed_data.py)
- **BDO Credit Card Application** (16 fields)
  - Fields: applicant info, employment status, card selection, file uploads
  - Conditional: Shows company_name for employed, business_name for self-employed
  - Shows account number only if existing_bdo_account is true

- **Maya Personal Loan** (15 fields)
  - Fields: personal info, loan details, income verification
  - Conditional: Uses all/any operators for complex logic
  - Shows bank statement only for non-Maya users with loan > 20000

- **Security Bank KYC** (16 fields)
  - Fields: client info, address, PEP declaration, document uploads
  - Conditional: Shows pep_details only if is_pep is true

### Frontend Changes
1. **CSS Design System** (`frontend/css/index.css`)
   - Added `.card-header`, `.card-body`, `.card-title` styles
   - Added `.activity-table` styles
   - Added `.profile-grid`, `.profile-section` styles
   - Added `.form-renderer` styles (form-input, form-select, etc.)
   - Added `.file-upload-wrapper` styles
   - Added loading states, skeleton, empty states

2. **Profile Page** (`frontend/profile.html`)
   - Removed inline styles
   - Uses standardized `.card-header`, `.card-body`, `.activity-table`
   - Consistent with other pages

3. **Form Renderer** (`frontend/js/FormRenderer.js`)
   - Rewritten to use design system CSS classes
   - Added file upload handling with token storage
   - Added `saveDraft()` and `validate()` methods

4. **Form Fill Page** (`frontend/form-fill.html`)
   - Removed inline styles
   - Uses template info banner
   - Consistent with design system

---

## Next Steps
1. Run `python backend/scripts/seed_data.py` to create templates
2. Test API endpoints with the new templates
3. Update README documentation
4. Add unit tests for validation engine

---
Last Updated: 2024

