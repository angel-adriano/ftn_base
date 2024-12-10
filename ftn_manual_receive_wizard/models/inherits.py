from odoo import models, fields, api

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def action_open_receive_wizard(self):
        # Trigger the wizard from purchase order
        self.ensure_one()  # Ensure only one purchase order is being processed at a time
        return self.env['receive.purchase.order.lines'].open_receive_wizard(self.id)

class ResCompany(models.Model):
    _inherit = 'res.company'

    auto_invoice_on_service = fields.Boolean(string="Auto Invoice Service Receipt")

class ConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    auto_invoice_on_service = fields.Boolean(readonly=False,related='company_id.auto_invoice_on_service',string="Auto Invoice Service Receipt")
