# Copyright 2026
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

import logging
from odoo import http, _
from odoo.http import request
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class PurchaseRequestPortalController(http.Controller):

    @http.route('/purchase/request/portal', type='http', auth='public', website=True, csrf=False)
    def purchase_request_portal_form(self, **kwargs):
        """Display the purchase request portal form"""
        departments = request.env['hr.department'].sudo().search([('company_id', '=', 3)])
        employees = request.env['hr.employee'].sudo().search([('company_id', '=', 3), ('active', '=', True)])
        uoms = request.env['uom.uom'].sudo().search([])

        values = {
            'departments': departments,
            'employees': employees,
            'uoms': uoms,
            'error': kwargs.get('error', ''),
            'success': kwargs.get('success', ''),
        }
        return request.render('purchase_request_portal.portal_form', values)

    @http.route('/purchase/request/portal/get_employees', type='jsonrpc', auth='public', csrf=False)
    def get_employees_by_department(self, department_id, **kwargs):
        """Get employees filtered by department"""
        if not department_id:
            return []

        employees = request.env['hr.employee'].sudo().search([
            ('department_id', '=', int(department_id))
        ])

        return [{
            'id': emp.id,
            'name': emp.name,
        } for emp in employees]

    @http.route('/purchase/request/portal/get_uoms', type='jsonrpc', auth='public', csrf=False)
    def get_uoms(self, **kwargs):
        """Get list of UoMs"""
        uoms = request.env['uom.uom'].sudo().search([])
        return [{
            'id': uom.id,
            'name': uom.name,
        } for uom in uoms]

    @http.route('/purchase/request/portal/submit', type='http', auth='public', website=True, methods=['POST'], csrf=False)
    def purchase_request_portal_submit(self, **post):
        """Handle purchase request submission from portal"""
        try:
            _logger.info('Purchase request portal submission started')
            _logger.info(f'POST data keys: {list(post.keys())}')
            _logger.info(f'POST data: {post}')

            # Validate required fields
            department_id = post.get('department_id')
            employee_id = post.get('employee_id')
            date_required = post.get('date_required')

            if not department_id or not employee_id or not date_required:
                _logger.warning('Missing required fields in portal submission')
                return request.redirect('/purchase/request/portal?error=missing_fields')

            # Parse request lines
            # We need to check all possible indices, not break on first gap
            # because users can delete lines creating gaps in numbering
            lines_data = []
            max_lines = 100  # reasonable maximum to prevent infinite loops

            for line_index in range(max_lines):
                product_name = post.get(f'line_name_{line_index}')

                # Skip empty lines (gaps from deleted lines)
                if not product_name:
                    continue

                product_qty = post.get(f'line_qty_{line_index}')
                product_uom_id = post.get(f'line_uom_{line_index}')

                if product_name and product_qty and product_uom_id:
                    lines_data.append((0, 0, {
                        'name': product_name,
                        'product_qty': float(product_qty),
                        'product_uom_id': int(product_uom_id),
                        'date_required': date_required,
                    }))
                    _logger.info(f'Line {line_index} added: {product_name}, qty: {product_qty}')

            _logger.info(f'Total lines parsed: {len(lines_data)}')

            if not lines_data:
                _logger.warning('No lines found in portal submission')
                return request.redirect('/purchase/request/portal?error=no_lines')

            # Create purchase request with employee_id
            # The model will auto-set department, assigned_to, and requested_by
            purchase_request_vals = {
                'department_id': int(department_id),
                'employee_id': int(employee_id),
                'line_ids': lines_data,
                'origin': 'Employee Portal',
            }

            # Add description if provided
            description = post.get('description')
            if description:
                purchase_request_vals['description'] = description

            purchase_request = request.env['purchase.request'].sudo().create(purchase_request_vals)
            _logger.info(f'Purchase request created: {purchase_request.name}')

            #Submit the purchase request for approval
            purchase_request.button_to_approve()
            _logger.info(f'Purchase request {purchase_request.name} submitted for approval')

            return request.redirect('/purchase/request/portal?success=1')

        except Exception as e:
            _logger.error(f'Error submitting purchase request from portal: {str(e)}', exc_info=True)
            return request.redirect('/purchase/request/portal?error=submission_failed')

