# Purchase Request Portal - Installation & Usage Guide (Odoo 19)

## Module Information

- **Name**: Purchase Request Portal
- **Version**: 19.0.1.0.0
- **Category**: Purchase Management
- **License**: LGPL-3.0
- **Author**: FTNMX

## Description

This module allows employees to submit purchase requests through a public web portal without requiring user registration. It's designed for organizations where not all employees have Odoo user accounts but still need to request purchases.

## Features

✨ **Public Portal Form**: Accessible without login
🏢 **Department Management**: Filter employees by department
👤 **Employee Selection**: Link purchase requests to specific employees
📋 **Dynamic Request Lines**: Add multiple products/items to request
📅 **Date Required**: Specify when items are needed
💬 **Notes Field**: Add additional information
🔔 **Automatic Notifications**: Notify department managers or configured users
✅ **Auto-approval Workflow**: Automatically submit requests for approval

## Installation

### Prerequisites

Ensure these modules are installed:
- `purchase_request` (OCA module, Odoo 19 version)
- `hr` (Human Resources)
- `portal` (Portal framework)
- `web` (Web framework)

### Installation Steps

1. **Copy Module**
   ```bash
   # Copy the module to your addons directory
   cp -r purchase_request_portal /path/to/odoo/addons/
   ```

2. **Update Apps List**
   - Go to Apps menu
   - Click "Update Apps List"
   - Search for "Purchase Request Portal"

3. **Install Module**
   - Click "Install" button
   - Wait for installation to complete

4. **Configure Settings**
   - Go to Purchase → Configuration → Settings
   - Scroll to "Purchase Request Portal" section
   - Set the notification user (who receives alerts when requests are submitted)
   - Save settings

## Configuration

### 1. Access Rights

The module automatically grants public users access to:
- Purchase Requests (read, create)
- Purchase Request Lines (read, create)
- HR Departments (read only)
- HR Employees (read only)
- UoM Units (read only)

### 2. Notification User

Set up who receives notifications:
1. Navigate to: **Purchase → Configuration → Settings**
2. Find: **Purchase Request Portal** section
3. Select: **Purchase Request Notification User**
4. Save

### 3. Department Managers

For automatic assignment to work:
1. Go to: **Employees → Departments**
2. For each department, set a **Manager**
3. Ensure the manager has a linked **User** account
4. Purchase requests will auto-assign to department managers

## Usage

### For Employees (Portal Users)

#### Accessing the Portal

1. Navigate to: `http://your-odoo-domain.com/purchase/request/portal`
2. No login required!

#### Submitting a Request

1. **Select Department**: Choose your department from dropdown
2. **Select Employee**: Choose your name (filtered by department)
3. **Date Required**: When do you need the items?
4. **Add Request Lines**:
   - Click "Add Line" button
   - Enter product/description
   - Enter quantity
   - Select unit of measure (UoM)
   - Click "Add Line" again for more items
5. **Add Notes** (optional): Additional information
6. **Submit**: Click "Submit Request" button

#### Success & Error Messages

- ✅ **Success**: "Your purchase request has been submitted successfully"
- ❌ **Missing Fields**: "Please fill in all required fields"
- ❌ **No Lines**: "Please add at least one product line"
- ❌ **Submission Failed**: "Submission failed. Please try again or contact support"

### For Managers (Backend Users)

#### Viewing Requests

1. Go to: **Purchase → Purchase Requests**
2. Look for requests with:
   - Origin: "Employee Portal"
   - Employee field populated
   - Status: "To Approve"

#### Request Details

Each portal-submitted request shows:
- **Employee**: Who submitted the request
- **Department**: Employee's department
- **Requested By**: Linked user (if employee has user account)
- **Assigned To**: Department manager (auto-assigned)
- **Origin**: "Employee Portal"

#### Approval Workflow

1. Review the request details
2. Check request lines
3. Approve or reject as per normal process
4. System tracks all changes in chatter

## Technical Details

### Portal URL

- **Main Form**: `/purchase/request/portal`
- **Submit Handler**: `/purchase/request/portal/submit` (POST)
- **Get Employees**: `/purchase/request/portal/get_employees` (JSON)
- **Get UoMs**: `/purchase/request/portal/get_uoms` (JSON)

### Model Extensions

**purchase.request**:
- New field: `employee_id` (Many2one to hr.employee)
- Auto-fill: department and assigned_to from employee
- Auto-submit: Calls `button_to_approve()` after creation

### Automatic Behaviors

1. **Department Auto-fill**: When employee selected, department auto-fills
2. **Manager Assignment**: Department manager becomes assigned_to
3. **User Linking**: If employee has user, becomes requested_by
4. **Notification**: Activity created for assigned user
5. **Auto-approve**: Request automatically submitted for approval

### Security Model

Public users can:
- ✅ View departments, employees, UoMs (read-only)
- ✅ Create purchase requests and lines
- ❌ Cannot edit existing requests
- ❌ Cannot delete requests
- ❌ Cannot approve/reject requests

## Customization

### CSS Styling

Custom styles in: `static/src/css/portal.css`

To customize:
1. Edit the CSS file
2. Restart Odoo or update assets
3. Clear browser cache

### Template Modifications

Template ID: `purchase_request_portal.portal_form`

To modify:
1. Inherit the template in your custom module
2. Use XPath to modify sections
3. Update and test

### Email Notifications

To add email notifications:
1. Create email template
2. Modify `_send_notification()` method
3. Add `mail_template.send_mail()` call

## Troubleshooting

### Issue: Portal form not accessible

**Solution**:
- Check URL is correct: `/purchase/request/portal`
- Verify module is installed
- Check website is published

### Issue: Employees not showing after department selection

**Solution**:
- Verify employees are assigned to departments
- Check browser console for JavaScript errors
- Clear browser cache

### Issue: Request created but no notification

**Solution**:
- Check notification user is configured in settings
- Verify department manager has user account
- Check chatter for messages

### Issue: Form submission fails

**Solution**:
- Check all required fields are filled
- Verify at least one line is added
- Check Odoo logs for errors
- Ensure dependencies are installed

### Issue: Bootstrap styling looks wrong

**Solution**:
- Module uses Bootstrap 5
- Clear browser cache
- Check for CSS conflicts with other modules
- Verify assets are loaded correctly

## API Integration (Optional)

### Create Request via Code

```python
# Create purchase request from code
request_vals = {
    'employee_id': employee_id,
    'department_id': department_id,
    'line_ids': [(0, 0, {
        'name': 'Product Description',
        'product_qty': 5.0,
        'product_uom_id': uom_id,
        'date_required': '2026-05-20',
    })],
    'origin': 'API Integration',
}
request = env['purchase.request'].sudo().create(request_vals)
request.button_to_approve()  # Submit for approval
```

## Upgrade Notes

### From Previous Versions

If upgrading from Odoo 14:
1. See `MIGRATION_V14_TO_V19.md` for detailed changes
2. Backup database before upgrade
3. Test thoroughly in staging environment
4. Review custom modifications

## Support

- **Documentation**: See `MIGRATION_V14_TO_V19.md` for technical details
- **Quick Reference**: See `MIGRATION_QUICK_REFERENCE.md`
- **Website**: https://www.formalizatunegoio.com
- **License**: LGPL-3.0

## Best Practices

1. ✅ **Regular Backups**: Always backup before changes
2. ✅ **Test Environment**: Test in staging before production
3. ✅ **Access Control**: Monitor public access for abuse
4. ✅ **User Training**: Train employees on portal usage
5. ✅ **Manager Assignment**: Keep department managers updated
6. ✅ **Regular Review**: Review submitted requests regularly

## Changelog

### Version 19.0.1.0.0 (2026-05-13)
- ✨ Migrated from Odoo 14 to Odoo 19
- 🔧 Updated to Bootstrap 5
- 🔧 Replaced deprecated `attrs` with modern attributes
- 🔧 Updated message types for compatibility
- 📝 Improved documentation

### Version 14.0.1.0.0
- 🎉 Initial release for Odoo 14

## License

LGPL-3.0 License

Copyright 2026 FTNMX

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

