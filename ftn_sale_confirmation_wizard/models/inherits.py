# -*- coding: utf-8 -*-

from odoo import models, fields

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    text_addenda = fields.Char(string="Text Addenda")

    def action_confirm(self):
        if self.env.context.get('skip_wizard'):
            # Original action_confirm logic
            return super(SaleOrder, self).action_confirm()

        # Trigger wizard if not skipped
        wizard = self.env['sale.order.wizard'].create({})
        return {
            'name': 'Confirm Sale Order',
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'active_id': self.id,
                'default_purchase_order': self.text_addenda,
                'default_project_name': self.client_order_ref,
                'default_analytic_account_id': self.analytic_account_id.id,
            },
        }
