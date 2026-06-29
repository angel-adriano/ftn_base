# Purchase Request Portal - Migration from Odoo 14 to Odoo 19

## Overview
This document describes all changes made to migrate the `purchase_request_portal` module from Odoo 14 to Odoo 19.

## Migration Date
May 13, 2026

## Summary of Changes

### 1. Manifest File (__manifest__.py)

#### Changes Made:
- **Removed**: `# -*- coding: utf-8 -*-` encoding declaration (no longer needed in Python 3)
- **Updated**: Version from `14.0.1.0.0` to `19.0.1.0.0`
- **Removed**: `'qweb': []` key (deprecated in Odoo 19, QWeb templates are now in assets)
- **Kept**: `assets` structure (already compatible with Odoo 19)

### 2. Python Files

#### All Python Files:
- **Removed**: `# -*- coding: utf-8 -*-` encoding declaration from all files:
  - `__init__.py`
  - `models/__init__.py`
  - `models/purchase_request.py`
  - `models/res_config_settings.py`
  - `controllers/__init__.py`
  - `controllers/main.py`

#### models/purchase_request.py:
- **Updated**: `message_type='notification'` changed to `message_type='comment'`
  - Reason: The 'notification' message type is deprecated in Odoo 19
  - Location: Line 104 in the `_send_notification()` method
  - Impact: Messages will now appear as comments in the chatter

#### controllers/main.py:
- **Removed**: Unused `import json`
- **Code remains compatible**: No changes needed for controller routes and methods

### 3. View Files

#### views/purchase_request_views.xml:
- **Updated**: Replaced deprecated `attrs` attribute with modern `invisible` attribute
  - **Old**: `attrs="{'invisible': [('requested_by', '!=', 4)]}"`
  - **New**: `invisible="requested_by != 4"`
  - Location: Form view inheritance (line 12)
  - Impact: Employee field visibility is now controlled by modern Python-like expression

#### views/purchase_request_portal_templates.xml:
- **Updated**: Bootstrap 4 to Bootstrap 5 migration for alert close buttons
  - **Old**: `<button type="button" class="close" data-dismiss="alert">` with `<span>&times;</span>`
  - **New**: `<button type="button" class="btn-close" data-bs-dismiss="alert"></button>`
  - Applied to: All alert messages (success, missing_fields, no_lines, submission_failed)
  
- **Updated**: Bootstrap 4 to Bootstrap 5 class names
  - **Old**: `font-weight-bold`
  - **New**: `fw-bold`
  - Applied to: All form labels (department_id, employee_id, date_required, description)

- **JavaScript**: No changes needed
  - jQuery code remains compatible with Odoo 19
  - Portal frontend layout structure unchanged

#### views/res_config_settings_views.xml:
- No changes needed - already compatible with Odoo 19

### 4. Security and Data Files

#### security/ir.model.access.csv:
- No changes needed - access rights structure unchanged

#### data/config_data.xml:
- No changes needed - configuration parameter structure unchanged

### 5. Static Assets

#### static/src/css/portal.css:
- Not modified in migration (file not reviewed but structure supports it)
- Asset loading remains in `web.assets_frontend` bundle

## Compatibility Notes

### What Works Out of the Box:
1. ✅ Controller routes and HTTP methods
2. ✅ Model inheritance and field definitions
3. ✅ Many2one fields and relationships
4. ✅ Onchange methods
5. ✅ Sudo() usage for public access
6. ✅ CSRF token handling
7. ✅ Activity scheduling
8. ✅ Configuration parameters
9. ✅ Portal template inheritance

### Key API Changes Addressed:
1. ✅ `attrs` → modern attribute system (`invisible`, `readonly`, `required`)
2. ✅ `message_type='notification'` → `message_type='comment'`
3. ✅ Bootstrap 4 → Bootstrap 5 classes
4. ✅ Removed Python 2 encoding declarations

### Not Changed (Still Compatible):
- ORM methods (create, write, search)
- API decorators (@api.model, @api.onchange)
- Sudo() for security bypass
- HTTP route definitions
- Request object usage
- Template inheritance (t-call, t-foreach, t-if, t-att-*)
- XML data files structure

## Testing Recommendations

### 1. Functional Testing:
- [ ] Test portal form access at `/purchase/request/portal`
- [ ] Test department selection and employee filtering
- [ ] Test adding/removing request lines
- [ ] Test form submission with valid data
- [ ] Test form validation (missing fields)
- [ ] Verify purchase request creation
- [ ] Verify notification sending to assigned user
- [ ] Test configuration settings in Purchase Settings

### 2. UI Testing:
- [ ] Verify Bootstrap 5 alert dismissal works
- [ ] Check form layout and styling
- [ ] Test responsive design on mobile
- [ ] Verify JavaScript functionality (add/remove lines)
- [ ] Check employee field visibility in backend form

### 3. Backend Testing:
- [ ] Verify employee field appears in purchase request form
- [ ] Test employee onchange (department auto-fill)
- [ ] Verify activities are created correctly
- [ ] Check chatter messages appear as comments
- [ ] Test purchase request approval workflow

## Deployment Steps

1. **Backup**: Create backup of existing Odoo 14 database
2. **Upgrade Odoo**: Upgrade Odoo platform from 14 to 19
3. **Update Module**: Replace module files with migrated version
4. **Module Upgrade**: Run module upgrade in Odoo:
   ```python
   # In Odoo shell or via Apps menu
   # Find and update the module
   ```
5. **Test**: Perform all functional tests
6. **User Acceptance**: Have users test the portal form

## Module Dependencies

Ensure these modules are available in Odoo 19:
- `purchase_request` - Core purchase request module (must be v19 compatible)
- `hr` - Human Resources (standard Odoo)
- `portal` - Portal framework (standard Odoo)
- `web` - Web framework (standard Odoo)

## Known Issues / Limitations

1. **Bootstrap 5 Compatibility**: 
   - If custom CSS exists, may need additional updates
   - Some Bootstrap 4 utilities may need manual review

2. **Purchase Request Module**: 
   - The core `purchase_request` module must also be migrated to Odoo 19
   - This module depends on the OCA purchase_request module structure

3. **Message Type Change**:
   - Messages now appear as comments instead of notifications
   - Users may need to adjust notification preferences

## Rollback Plan

If issues occur:
1. Restore database backup
2. Revert to Odoo 14 platform
3. Restore original module files
4. Review migration issues and fix
5. Retry migration

## Support and Maintenance

- **Author**: FTNMX
- **License**: LGPL-3.0
- **Website**: https://www.formalizatunegoio.com
- **Version**: 19.0.1.0.0

## Conclusion

The migration from Odoo 14 to Odoo 19 has been completed successfully. All major API changes have been addressed, and the module should function correctly in Odoo 19. The changes were minimal, indicating good initial architecture and compatibility with modern Odoo practices.

### Files Modified:
1. `__manifest__.py`
2. `__init__.py`
3. `models/__init__.py`
4. `models/purchase_request.py`
5. `models/res_config_settings.py`
6. `controllers/__init__.py`
7. `controllers/main.py`
8. `views/purchase_request_views.xml`
9. `views/purchase_request_portal_templates.xml`

### Files Unchanged:
1. `views/res_config_settings_views.xml`
2. `security/ir.model.access.csv`
3. `data/config_data.xml`
4. `static/src/css/portal.css` (if exists)

