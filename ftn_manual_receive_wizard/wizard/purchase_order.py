from odoo import api, fields, models

class ReceivePurchaseOrderLines(models.TransientModel):
    _name = 'receive.purchase.order.lines'
    _description = 'Receive Purchase Order Lines'

    purchase_order_id = fields.Many2one('purchase.order', string='Purchase Order', required=True)
    line_ids = fields.One2many('receive.purchase.order.line.wizard', 'wizard_id', string='Order Lines')

    @api.model
    def default_get(self, fields):
        res = super(ReceivePurchaseOrderLines, self).default_get(fields)
        purchase_order_ids = self._context.get('active_ids')
        if not purchase_order_ids or len(purchase_order_ids) != 1:
            return res  # Ensure only one purchase order is being handled

        purchase_order = self.env['purchase.order'].browse(purchase_order_ids[0])
        lines = []
        for line in purchase_order.order_line:
            if line.qty_received_method == 'manual':
                lines.append((0, 0, {
                    'purchase_order_line_id': line.id,
                    'product_id': line.product_id.id,
                    'product_uom': line.product_uom.id,
                    'qty_ordered': line.product_qty,
                    'qty_received': line.qty_received,
                }))
        res.update({'purchase_order_id': purchase_order.id, 'line_ids': lines})
        return res

    def action_receive_lines(self):
        for wizard_line in self.line_ids:
            if wizard_line.qty_to_receive > 0:
                if not wizard_line.purchase_order_line_id:
                    raise models.ValidationError("Purchase Order Line is missing for the selected line.")

                # Update qty_received in purchase.order.line
                wizard_line.purchase_order_line_id.qty_received += wizard_line.qty_to_receive

        if self.purchase_order_id.company_id.auto_invoice_on_service and self.purchase_order_id.invoice_status == 'to invoice':
            # Trigger action to create the vendor bill (invoice)
            return self.purchase_order_id.action_create_invoice()

    @api.model
    def open_receive_wizard(self, purchase_order_id):
        return {
            'name': 'Receive Purchase Order Lines',
            'type': 'ir.actions.act_window',
            'res_model': 'receive.purchase.order.lines',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_purchase_order_id': purchase_order_id,
                'active_id': purchase_order_id,
                'active_ids': [purchase_order_id],
            },
        }


class ReceivePurchaseOrderLineWizard(models.TransientModel):
    _name = 'receive.purchase.order.line.wizard'
    _description = 'Receive Purchase Order Line Wizard'

    wizard_id = fields.Many2one('receive.purchase.order.lines', string='Wizard', required=True, ondelete='cascade')
    purchase_order_line_id = fields.Many2one('purchase.order.line', string='Purchase Order Line', required=True)
    product_id = fields.Many2one('product.product', string='Product', required=True)
    product_uom = fields.Many2one('uom.uom', string='Unit of Measure', required=True)
    qty_ordered = fields.Float(string='Ordered Quantity', readonly=True)
    qty_received = fields.Float(string='Already Received', readonly=True)
    qty_to_receive = fields.Float(string='Quantity to Receive')

    # @api.constrains('qty_to_receive')
    # def _check_qty_to_receive(self):
    #     for line in self:
    #         if line.qty_to_receive < 0:
    #             raise models.ValidationError("Quantity to receive cannot be negative.")
    #         if line.qty_to_receive + line.qty_received > line.qty_ordered:
    #             raise models.ValidationError("Total received quantity cannot exceed the ordered quantity.")
