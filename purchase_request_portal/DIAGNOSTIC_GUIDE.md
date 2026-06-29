# Diagnostic Steps for "No Lines" Issue

## Current Status

The logs show:
- ✅ Controller is being called
- ✅ Logging is working
- ❌ **Total lines parsed: 0** ← The problem

This means the POST data either:
1. Doesn't contain line fields at all, OR
2. Has different field names than expected

## What I've Added

### 1. Server-Side Logging
Added to `controllers/main.py`:
```python
_logger.info(f'POST data keys: {list(post.keys())}')
_logger.info(f'POST data: {post}')
```

This will show EXACTLY what data the server receives.

### 2. Client-Side Validation
Added to `purchase_request_portal_templates.xml`:
```javascript
function validateForm() {
    console.log('=== Form Submission Validation ===');
    // Logs all line inputs before submission
}
```

This will show what fields exist in the form.

### 3. Fixed Deprecation Warnings
Changed `type='json'` → `type='jsonrpc'` for Odoo 19 compatibility.

## How to Test

### Step 1: Restart Odoo
```bash
# If using systemctl
sudo systemctl restart odoo

# If using docker
docker restart odoo_container_name
```

### Step 2: Open Browser Console
1. Navigate to `/purchase/request/portal`
2. Press F12 to open Developer Tools
3. Go to "Console" tab
4. Keep it open while testing

### Step 3: Fill Form and Submit
1. Select department
2. Select employee
3. Click "Add Line" (at least once)
4. Fill in:
   - Product/Description
   - Quantity
   - Unit of Measure
5. Click "Submit Request"

### Step 4: Check Browser Console
You should see:
```
=== Form Submission Validation ===
Total line name inputs found: 2
Line input: line_name_0 = Test Product
Line input: line_name_1 = Another Product
Form validation passed, submitting...
```

**If you DON'T see these messages:**
- JavaScript isn't running
- Lines aren't being added to the form

### Step 5: Check Odoo Logs
Look for:
```
INFO ... Purchase request portal submission started
INFO ... POST data keys: ['csrf_token', 'department_id', 'employee_id', 'date_required', 'line_name_0', 'line_qty_0', 'line_uom_0', ...]
INFO ... POST data: {'department_id': '5', 'employee_id': '10', ...}
```

## Possible Issues & Solutions

### Issue 1: No line fields in POST data
**Symptoms:**
- Browser console shows fields exist
- Logs show POST data WITHOUT line_name_*, line_qty_*, line_uom_*

**Cause:** Form fields are outside the `<form>` tag or being removed

**Solution:** Check the container `#request_lines_container` is inside the form

### Issue 2: Fields have wrong names
**Symptoms:**
- POST data has fields but with different names

**Cause:** JavaScript uses different naming

**Solution:** Look at POST data keys and adjust controller to match

### Issue 3: JavaScript not running
**Symptoms:**
- No console messages
- Can't add/remove lines

**Cause:** jQuery not loaded or JavaScript error

**Solution:** Check browser console for errors

### Issue 4: Fields are empty
**Symptoms:**
- POST has line_name_0, line_qty_0, etc. but they're all empty strings

**Cause:** User didn't fill fields OR fields lost values on submit

**Solution:** Make sure "required" attribute is working

## Expected Behavior After Fix

### Browser Console:
```
=== Form Submission Validation ===
Total line name inputs found: 2
Line input: line_name_0 = Test Product 1
Line input: line_name_1 = Test Product 2
Form validation passed, submitting...
```

### Odoo Logs:
```
INFO ... Purchase request portal submission started
INFO ... POST data keys: ['csrf_token', 'department_id', 'employee_id', 'date_required', 'description', 'line_name_0', 'line_qty_0', 'line_uom_0', 'line_name_1', 'line_qty_1', 'line_uom_1']
INFO ... Line 0 added: Test Product 1, qty: 5.0
INFO ... Line 1 added: Test Product 2, qty: 3.0
INFO ... Total lines parsed: 2
INFO ... Purchase request created: PR00001
INFO ... Purchase request PR00001 submitted for approval
```

### Result:
```
✅ Redirected to: /purchase/request/portal?success=1
```

## What to Share

After testing, please share:

1. **Browser Console Output** (copy/paste or screenshot)
2. **Odoo Log Lines** starting with "Purchase request portal submission started"
3. **What happens** when you submit the form

This will tell us exactly where the problem is!

## Quick Check: Is the Form Structure Correct?

Open browser console and run:
```javascript
// Check if add line button exists
console.log('Add line button:', $('#add_line_btn').length);

// Check if container exists
console.log('Lines container:', $('#request_lines_container').length);

// Check if container is inside form
console.log('Container inside form:', $('#purchase_request_form').find('#request_lines_container').length);

// Try adding a line manually
$('#add_line_btn').trigger('click');

// Check if line was added
console.log('Lines after click:', $('input[name^="line_name_"]').length);
```

If the last line shows `0`, the JavaScript isn't working properly.

---

**Status:** More diagnostics added, waiting for test results

