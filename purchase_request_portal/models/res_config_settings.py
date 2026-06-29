# Copyright 2026
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    approver_type = fields.Selection([
        ('department', 'Department Manager'),
        ('fixed', 'Fixed User'),
    ],
        string='Purchase Request Approver Type',
        default='department',
        config_parameter='purchase_request_portal.approver_type_id',
        help='Defines who will be assigned to approve purchase requests from the portal:\n'
             '- Department Manager: Assign to the employee\'s department manager\n'
             '- Fixed User: Assign to the user configured below'
    )

    purchase_request_notification_user_id = fields.Many2one(
        'res.users',
        string='Fixed Approver / Notification User',
        config_parameter='purchase_request_portal.notification_user_id',
        help='User who will be assigned to approve requests (when Approver Type is "Fixed User") '
             'and receive notifications when a purchase request is submitted via the portal',
    )
