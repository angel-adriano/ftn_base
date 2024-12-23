from odoo import models, fields, api

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    has_service = fields.Boolean(string="Incluye servicios", compute="get_has_service")

    def get_has_service(self):
        for po in self:
            if po.order_line:
                po.has_service = any(line.has_service for line in po.order_line)

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

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    has_service = fields.Boolean(compute='set_service_flag')

    def set_service_flag(self):
        for line in self:
            if line.product_id.detailed_type == 'service':
                line.has_service = True
            else:
                line.has_service = False
