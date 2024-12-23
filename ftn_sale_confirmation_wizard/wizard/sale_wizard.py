from odoo import models, fields, api

class SaleOrderWizard(models.TransientModel):
    _name = 'sale.order.wizard'
    _description = 'Sale Order Wizard'

    purchase_order = fields.Char(string="Purchase Order")
    project_name = fields.Char(string="Project Name")
    analytic_account_id = fields.Many2one('account.analytic.account', string="Analytic Account")
    attachment_pdf = fields.Binary(string="Attachment (PDF)")
    attachment_name = fields.Char(string="Attachment Filename", default='Purchase order')

    def action_apply(self):
        active_id = self.env.context.get('active_id')
        sale_order = self.env['sale.order'].browse(active_id)

        if sale_order:
            sale_order.write({
                'text_addenda': self.purchase_order,
                'client_order_ref': self.project_name,
                'analytic_account_id': self.analytic_account_id.id,
            })

            if self.attachment_pdf:
                self.env['ir.attachment'].create({
                    'name': self.attachment_name or "Purchase_order.pdf",
                    'type': 'binary',
                    'datas': self.attachment_pdf,
                    'res_model': 'sale.order',
                    'res_id': sale_order.id,
                })

            # Call the original action_confirm logic
            sale_order.with_context(skip_wizard=True).sudo().action_confirm()
