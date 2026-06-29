# -*- coding: utf-8 -*-
# Copyright 2026
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo import api, fields, models, _


class PurchaseRequest(models.Model):
    _inherit = "purchase.request"

    employee_id = fields.Many2one(
        comodel_name="hr.employee",
        string="Employee",
        help="Employee who requested this purchase",
        tracking=True,
    )

    # @api.onchange('employee_id')
    # def _onchange_employee_id(self):
    #     """When employee changes, update department and assigned_to"""
    #     for rec in self:
    #         if rec.employee_id:
    #             # Set department from employee
    #             if rec.employee_id.department_id:
    #                 rec.department_id = rec.employee_id.department_id
    #
    #                 # Set assigned_to from department manager
    #                 if rec.employee_id.department_id.manager_id and rec.employee_id.department_id.manager_id.user_id:
    #                     rec.assigned_to = rec.employee_id.department_id.manager_id.user_id
    #                 else:
    #                     rec.assigned_to = False
    #             else:
    #                 rec.department_id = False
    #                 rec.assigned_to = False
    #
    #             # Set requested_by from employee's user if exists
    #             if rec.employee_id.user_id:
    #                 rec.requested_by = rec.employee_id.user_id
    #         else:
    #             # If employee is cleared, reset fields
    #             rec.department_id = False
    #             rec.assigned_to = False

    @api.onchange("requested_by")
    def onchange_requested_by(self):
        if self.requested_by != 4:  # if not portal user
            employee = self.env['hr.employee'].search([('user_id', '=', self.requested_by.id)])
            if employee:
                self.department_id = employee.department_id.id

                # Get approver type configuration
                config_param = self.env['ir.config_parameter'].sudo()
                approver_type = config_param.get_param('purchase_request_portal.approver_type_id', 'department')

                if approver_type == 'department':
                    # Use department manager
                    if employee.department_id and employee.department_id.manager_id:
                        self.assigned_to = employee.department_id.manager_id.user_id.id
                    else:
                        self.assigned_to = False
                elif approver_type == 'fixed':
                    # Use configured notification user
                    notification_user_id = config_param.get_param('purchase_request_portal.notification_user_id')
                    if notification_user_id:
                        self.assigned_to = int(notification_user_id)
                    else:
                        self.assigned_to = False

                self.employee_id = employee.id

    @api.model_create_multi
    def create(self, vals_list):
        """Auto-set department and assigned_to from employee on create"""
        # In Odoo 19, create receives a list of dicts, not a single dict
        for vals in vals_list:
            if vals.get('employee_id'):
                employee = self.env['hr.employee'].browse(vals['employee_id'])

                # Auto-set department from employee if not provided
                if not vals.get('department_id') and employee.department_id:
                    vals['department_id'] = employee.department_id.id

                # Auto-set assigned_to from department manager if not provided
                if not vals.get('assigned_to') and employee.department_id and employee.department_id.manager_id:
                    if employee.department_id.manager_id.user_id:
                        vals['assigned_to'] = employee.department_id.manager_id.user_id.id

                # Auto-set requested_by from employee's user if not provided
                if not vals.get('requested_by') and employee.user_id:
                    vals['requested_by'] = employee.user_id.id

        return super(PurchaseRequest, self).create(vals_list)

    def button_to_approve(self):
        """Override to send notification when request is submitted for approval"""
        res = super(PurchaseRequest, self).button_to_approve()

        # Send notification after the request is submitted for approval
        self._send_notification()

        return res

    def _send_notification(self):
        """Send notification to assigned_to user or configured notification user"""
        self.ensure_one()

        notification_user = None

        # First priority: assigned_to user
        if self.assigned_to:
            notification_user = self.assigned_to
        else:
            # Fallback: configured notification user from system parameters
            config_param = self.env['ir.config_parameter'].sudo()
            notification_user_id = config_param.get_param('purchase_request_portal.notification_user_id')
            if notification_user_id:
                notification_user = self.env['res.users'].sudo().browse(int(notification_user_id))

        if notification_user and notification_user.exists():
            # Create activity or send message
            self.sudo().message_post(
                body=_('A new purchase request has been submitted via the employee portal.'),
                subject=_('New Purchase Request from Portal'),
                message_type='comment',
                partner_ids=[notification_user.partner_id.id],
            )

            # Create activity
            self.sudo().activity_schedule(
                'mail.mail_activity_data_todo',
                user_id=notification_user.id,
                summary=_('New Purchase Request from Portal'),
                note=_('Purchase Request %s has been submitted via the employee portal. Please review.') % self.name,
            )


    def write(self, vals):
        """Auto-update department and assigned_to when employee changes"""
        if vals.get('employee_id'):
            employee = self.env['hr.employee'].browse(vals['employee_id'])

            # Get approver type configuration
            config_param = self.env['ir.config_parameter'].sudo()
            approver_type = config_param.get_param('purchase_request_portal.approver_type_id', 'department')
            notification_user_id = config_param.get_param('purchase_request_portal.notification_user_id')

            # Auto-set department from employee if not explicitly changed
            if 'department_id' not in vals and employee.department_id:
                vals['department_id'] = employee.department_id.id

            # Auto-set assigned_to based on approver type if not explicitly changed
            if 'assigned_to' not in vals:
                if approver_type == 'department':
                    # Use department manager
                    if employee.department_id and employee.department_id.manager_id:
                        if employee.department_id.manager_id.user_id:
                            vals['assigned_to'] = employee.department_id.manager_id.user_id.id
                elif approver_type == 'fixed':
                    # Use configured notification user
                    if notification_user_id:
                        vals['assigned_to'] = int(notification_user_id)

            # Auto-set requested_by from employee's user if not explicitly changed
            if 'requested_by' not in vals and employee.user_id:
                vals['requested_by'] = employee.user_id.id

        return super(PurchaseRequest, self).write(vals)
