# -*- coding: utf-8 -*-

from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def link_order_lines_to_invoices(self):
        for order in self:
            # Find all invoices with the same payment_reference as the sale order name
            invoices = self.env['account.move'].search([('payment_reference', '=', order.name)])
            if invoices:
                for order_line in order.order_line:
                    # Collect all matching invoice lines for the current order line's product
                    matching_invoice_lines = invoices.mapped('invoice_line_ids').filtered(
                        lambda line: line.product_id == order_line.product_id
                    )
                    # Link the order line to the matching invoice lines
                    order_line.invoice_lines = [(6, 0, matching_invoice_lines.ids)]
