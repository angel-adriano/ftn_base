# Bug Fix: Portal Form Lines Not Being Parsed

## Issue Description

Users were being redirected to `portal?error=no_lines` even when they had added multiple lines to the purchase request form.

## Root Cause

The controller was using a `while True` loop that would **break immediately** when it didn't find a line at a specific index:

```python
# OLD CODE (BUGGY)
line_index = 0
while True:
    product_name = post.get(f'line_name_{line_index}')
    if not product_name:
        break  # ❌ Breaks at first missing line!
    # ... process line
    line_index += 1
```

### Why This Failed

When users deleted lines from the DOM:
1. User adds Line 0, Line 1, Line 2
2. User removes Line 0 and Line 1  
3. Form now only has fields: `line_name_2`, `line_qty_2`, `line_uom_2`
4. Controller looks for `line_name_0`, doesn't find it, **breaks immediately**
5. Controller never checks for `line_name_2`
6. Result: `lines_data` is empty → redirect to error

## Solution

Changed to use a `for` loop with `continue` to skip gaps:

```python
# NEW CODE (FIXED)
max_lines = 100  # reasonable maximum
for line_index in range(max_lines):
    product_name = post.get(f'line_name_{line_index}')
    
    # Skip empty lines (gaps from deleted lines)
    if not product_name:
        continue  # ✅ Skip and check next index
    
    # ... process line
```

### How This Works

Now the controller:
1. Checks indices 0 through 99
2. **Skips** missing indices (from deleted lines)
3. Processes any valid lines it finds
4. Successfully captures all existing lines regardless of gaps

## Additional Improvements

### Added Logging

Added comprehensive logging to help debug future issues:

```python
import logging
_logger = logging.getLogger(__name__)

# Logs when submission starts
_logger.info('Purchase request portal submission started')

# Logs each line found
_logger.info(f'Line {line_index} added: {product_name}, qty: {product_qty}')

# Logs total lines parsed
_logger.info(f'Total lines parsed: {len(lines_data)}')

# Logs successful creation
_logger.info(f'Purchase request created: {purchase_request.name}')

# Logs errors with full traceback
_logger.error(f'Error submitting purchase request from portal: {str(e)}', exc_info=True)
```

### Benefits

1. **Easier debugging**: Check Odoo logs to see exactly what's happening
2. **Monitoring**: Track how many requests are submitted
3. **Error tracking**: Get full error details when submission fails

## Testing

After this fix, test the following scenarios:

### Test 1: Normal Usage
- [ ] Add 2-3 lines
- [ ] Submit form
- [ ] Verify purchase request created ✅

### Test 2: Delete First Line
- [ ] Add 3 lines
- [ ] Delete first line
- [ ] Submit form
- [ ] Verify purchase request created with 2 lines ✅

### Test 3: Delete Middle Line
- [ ] Add 3 lines
- [ ] Delete middle line
- [ ] Submit form
- [ ] Verify purchase request created with 2 lines ✅

### Test 4: Delete and Re-add
- [ ] Add line, delete it, add another
- [ ] Submit form
- [ ] Verify purchase request created ✅

## Files Modified

- `controllers/main.py`: Fixed line parsing logic and added logging

## Version

- **Fixed in**: 19.0.1.0.1
- **Date**: May 13, 2026

## Impact

- **Breaking Changes**: None
- **Database Changes**: None
- **User Impact**: Bug is fixed, users can now delete lines without issues

## Deployment

Simply update the `controllers/main.py` file and restart Odoo:
```bash
sudo systemctl restart odoo
```

No module upgrade needed (controller changes don't require upgrade).

## Verification

Check Odoo logs after fix:
```bash
# Follow Odoo logs
tail -f /var/log/odoo/odoo.log | grep "Purchase request portal"
```

You should see:
- "Purchase request portal submission started"
- "Line X added: ..." for each line
- "Total lines parsed: N"
- "Purchase request created: PR00XXX"
- "Purchase request PR00XXX submitted for approval"

---

**Status**: ✅ FIXED
**Tested**: Pending user verification
**Ready for deployment**: Yes

