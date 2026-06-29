# Approver Type Configuration - Feature Documentation

## Overview

The Purchase Request Portal module now supports **flexible approver assignment** through the new `approver_type` configuration parameter.

## Feature Description

### Two Approver Modes

#### 1. **Department Manager** (Default)
- Purchase requests are assigned to the **employee's department manager**
- Dynamic assignment based on organizational structure
- Best for: Organizations with clear department hierarchies

#### 2. **Fixed User**
- All purchase requests are assigned to a **single configured user**
- Centralized approval process
- Best for: Small organizations or centralized purchasing departments

## Configuration

### Access Settings

1. Navigate to: **Purchase → Configuration → Settings**
2. Scroll to: **Purchase Request Portal** section
3. Configure:
   - **Approver Type**: Select 'Department Manager' or 'Fixed User'
   - **Fixed Approver / Notification User**: Select the user (required for 'Fixed User' mode)

### Field Descriptions

| Field | Description |
|-------|-------------|
| **Approver Type** | Determines assignment logic:<br>- **Department Manager**: Assigns to employee's department manager<br>- **Fixed User**: Assigns to the configured user below |
| **Fixed Approver / Notification User** | User who:<br>- Receives approval assignment (in 'Fixed User' mode)<br>- Receives notifications in all modes<br>- Gets activities created for new requests |

## How It Works

### Portal Submission Flow

1. **Employee fills portal form**
   - Selects department and employee
   - Adds request lines
   - Submits request

2. **System checks approver_type configuration**

3. **If 'Department Manager':**
   ```
   Employee → Department → Manager → assigned_to field
   ```
   - Gets employee's department
   - Gets department's manager
   - Gets manager's user account
   - Sets as assigned_to

4. **If 'Fixed User':**
   ```
   Configuration → Fixed User → assigned_to field
   ```
   - Gets configured notification user
   - Sets as assigned_to
   - Independent of department structure

### Technical Implementation

The logic is implemented in multiple methods:

#### 1. **_onchange_employee_id** (UI onchange)
```python
if approver_type == 'department':
    # Use department manager
    rec.assigned_to = rec.employee_id.department_id.manager_id.user_id
elif approver_type == 'fixed':
    # Use configured user
    rec.assigned_to = notification_user_id
```

#### 2. **create()** (Record creation)
```python
for vals in vals_list:
    if approver_type == 'department':
        vals['assigned_to'] = department.manager_id.user_id.id
    elif approver_type == 'fixed':
        vals['assigned_to'] = notification_user_id
```

#### 3. **write()** (Record update)
```python
if approver_type == 'department':
    vals['assigned_to'] = department.manager_id.user_id.id
elif approver_type == 'fixed':
    vals['assigned_to'] = notification_user_id
```

#### 4. **onchange_requested_by** (Auto-fill from user)
```python
if approver_type == 'department':
    self.assigned_to = employee.department_id.manager_id.user_id.id
elif approver_type == 'fixed':
    self.assigned_to = notification_user_id
```

## Use Cases

### Scenario 1: Multi-Department Organization

**Configuration:**
- Approver Type: **Department Manager**

**Example:**
- Sales Department → Sales Manager receives requests from sales employees
- IT Department → IT Manager receives requests from IT employees
- Production Department → Production Manager receives requests from production employees

**Benefits:**
- ✅ Distributed approval responsibility
- ✅ Department managers control their budgets
- ✅ Faster approvals (no bottleneck)

### Scenario 2: Centralized Purchasing

**Configuration:**
- Approver Type: **Fixed User**
- Fixed Approver: John Smith (Purchasing Manager)

**Example:**
- All requests from any employee → John Smith
- Centralized purchasing decisions
- Uniform approval criteria

**Benefits:**
- ✅ Single point of control
- ✅ Consistent purchasing policies
- ✅ Better volume negotiation
- ✅ Centralized budget oversight

### Scenario 3: Hybrid Approach

**Initial Setup:**
- Approver Type: **Fixed User** during implementation phase

**After stabilization:**
- Change to: **Department Manager**
- Distribute responsibility to department heads

**Benefits:**
- ✅ Controlled rollout
- ✅ Training period with oversight
- ✅ Smooth transition to distributed model

## Backend Behavior

### Creating Purchase Request Manually

When creating a purchase request in the backend:

1. Select **Employee** field
2. System automatically fills:
   - Department (from employee)
   - Assigned To (based on approver_type)
   - Requested By (if employee has user account)

### Modifying Employee Field

When changing the employee:
- Department updates automatically
- Assigned To recalculates based on approver_type
- Previous assignments are overwritten

## Portal Behavior

From the portal (`/purchase/request/portal`):

1. User selects department and employee
2. On submission:
   - System reads approver_type configuration
   - Assigns request based on selected mode
   - Creates activity for assigned user
   - Sends notification

No user intervention needed - fully automatic!

## Notifications

### Who Receives Notifications?

**Notifications are sent to:**

1. **Assigned User** (primary)
   - Department Manager (in 'department' mode)
   - Fixed User (in 'fixed' mode)

2. **Fallback** (if no assigned_to):
   - Configured notification user
   - Ensures no request goes unnoticed

### Notification Content

- **Chatter Message**: Posted on the purchase request
- **Activity**: Created for the assigned user
- **Type**: "To Do" activity
- **Summary**: "New Purchase Request from Portal"
- **Note**: Request details and review prompt

## Configuration Examples

### Example 1: Small Company (10 employees)

**Setup:**
```
Approver Type: Fixed User
Fixed Approver: Maria Garcia (Owner)
```

**Result:**
- All 10 employees → Maria reviews everything
- Simple, centralized control

### Example 2: Medium Company (100 employees, 5 departments)

**Setup:**
```
Approver Type: Department Manager
Fixed Approver: Carlos Rodriguez (Purchasing Director) [for notifications]
```

**Result:**
- Sales requests → Sales Manager
- IT requests → IT Manager
- Production requests → Production Manager
- etc.
- Carlos receives notifications for visibility

### Example 3: Large Company (500 employees, 20 departments)

**Setup:**
```
Approver Type: Department Manager
Department Managers: Each department has a manager configured
Fixed Approver: Purchasing Team Lead [for orphaned requests]
```

**Result:**
- Each department handles own requests
- Scalable approval process
- No bottlenecks

## Troubleshooting

### Issue: No one assigned to request

**Cause:**
- Department Manager mode: Department has no manager configured
- Fixed User mode: No notification user configured

**Solution:**
1. Go to **Employees → Departments**
2. Set a Manager for each department
3. OR: Switch to Fixed User mode and configure a user

### Issue: Wrong person receiving requests

**Check:**
1. Current **Approver Type** setting
2. If 'Department': Check employee's department and department manager
3. If 'Fixed': Check configured notification user

**Fix:**
- Update department managers, OR
- Change approver type, OR
- Update configured notification user

### Issue: Requests not getting approved

**Verify:**
- Assigned user has proper access rights
- User is active in the system
- User receives notifications/activities
- Check user's activity inbox

## Migration Notes

### Upgrading from Previous Version

**Default Behavior:**
- New installations: Default to 'department' mode
- Upgrades: Maintains 'department' mode (preserves existing behavior)

**No action needed** unless you want to change to Fixed User mode.

### Changing Modes

**Impact on Existing Requests:**
- Already submitted requests: Keep current assigned_to
- New requests: Use new approver type

**Recommendation:**
- Test in staging environment first
- Communicate change to users
- Update department managers if needed

## Best Practices

### 1. Choose the Right Mode

| Factor | Department Manager | Fixed User |
|--------|-------------------|------------|
| Company Size | Medium to Large | Small |
| Department Structure | Well-defined | Flat |
| Approval Speed | Fast (distributed) | Slower (centralized) |
| Budget Control | Per department | Central |
| Purchasing Expertise | Distributed | Specialized |

### 2. Configure Properly

- ✅ **Always** set a notification user (fallback)
- ✅ Ensure department managers are updated
- ✅ Test both modes before deciding
- ✅ Document your choice for future reference

### 3. Monitor Usage

- Check if requests are being assigned correctly
- Monitor approval times
- Get feedback from approvers
- Adjust configuration as organization grows

## API Reference

### Configuration Parameters

```python
# Get approver type
approver_type = self.env['ir.config_parameter'].sudo().get_param(
    'purchase_request_portal.approver_type_id', 
    'department'  # default
)

# Get notification user
notification_user_id = self.env['ir.config_parameter'].sudo().get_param(
    'purchase_request_portal.notification_user_id'
)
```

### Programmatic Creation

```python
# Create purchase request with auto-assignment
pr = env['purchase.request'].create({
    'employee_id': employee_id,
    # assigned_to will be set automatically based on approver_type
    # department_id will be set from employee
})
```

## Summary

The Approver Type configuration provides:

✅ **Flexibility**: Choose between centralized or distributed approval
✅ **Automation**: No manual assignment needed
✅ **Scalability**: Works for organizations of any size
✅ **Simplicity**: One setting controls entire behavior
✅ **Reliability**: Fallback notification user ensures nothing is missed

---

**Version:** 19.0.1.0.2
**Date:** May 13, 2026
**Feature:** Approver Type Configuration

