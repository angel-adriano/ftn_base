# -*- coding: utf-8 -*-

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    so_delivery_status = fields.Selection([('to_be_deliver', 'To be Delivered'), ('partial_deliver', 'Partially Delivered'),
                                           ('delivered', 'Delivered')], string='Delivery Status', compute='_get_so_delivery_status', store=True)
    so_invoice_status = fields.Selection([('to_be_invoice', 'To Invoice'), ('partial_paid', 'Partially Paid'),
                                          ('posted', 'Paid')], string='SO Invoice Status', compute='_get_so_invoice_status', store=True)

    @api.depends('state', 'picking_ids.state')
    def _get_so_delivery_status(self):
        for rec in self:
            rec.so_delivery_status = ''
            if rec.picking_ids:
                if all(d.state == 'draft' for d in rec.picking_ids) or all(d.state == 'assigned' for d in rec.picking_ids) or all(d.state == 'confirmed' for d in rec.picking_ids):
                    rec.so_delivery_status = 'to_be_deliver'
                if any(d.state == 'draft' for d in rec.picking_ids) or any(d.state == 'assigned' for d in rec.picking_ids) or any(d.state == 'confirmed' for d in rec.picking_ids) and not any(d.state=='done' for d in rec.picking_ids):
                    rec.so_delivery_status = 'to_be_deliver'
                if all(d.state == 'done' for d in rec.picking_ids):
                    rec.so_delivery_status = 'delivered'
                if any(d.state == 'done' for d in rec.picking_ids) and any(d.state == 'assigned' for d in rec.picking_ids):
                    rec.so_delivery_status='partial_deliver'
                if any(d.state == 'done' for d in rec.picking_ids) and any(d.state == 'confirmed' for d in rec.picking_ids):
                    rec.so_delivery_status = 'partial_deliver'
                if any(d.state == 'done' for d in rec.picking_ids) and any(d.state == 'draft' for d in rec.picking_ids):
                    rec.so_delivery_status = 'partial_deliver'
                if any(d.state == 'done' for d in rec.picking_ids) and any(d.state == 'cancel' for d in rec.picking_ids) and not any(d.state == 'confirmed' for d in rec.picking_ids) and not any(d.state == 'assigned' for d in rec.picking_ids):
                    rec.so_delivery_status = 'delivered'

    @api.depends('state', 'invoice_ids.state', 'invoice_ids.amount_residual')
    def _get_so_invoice_status(self):
        for rec in self:
            rec.so_invoice_status = ''
            if rec.invoice_ids:
                if all(i.state == 'draft' for i in rec.invoice_ids):
                    rec.so_invoice_status = 'to_be_invoice'
                if any(i.state == 'draft' for i in rec.invoice_ids) or any(i.state == 'posted' for i in rec.invoice_ids) and (i.amount_total == i.amount_residual for i in rec.invoice_ids):
                    rec.so_invoice_status = 'to_be_invoice'
                if any(i.state == 'draft' for i in rec.invoice_ids) and any(i.amount_total == i.amount_residual for i in rec.invoice_ids) and not any(i.state == 'posted' for i in rec.invoice_ids):
                    rec.so_invoice_status = 'to_be_invoice'
                if any(i.amount_residual > 0.00 for i in rec.invoice_ids) and any(i.amount_residual < i.amount_total for i in rec.invoice_ids) and any(i.state == 'posted' for i in rec.invoice_ids):
                    rec.so_invoice_status = 'partial_paid'
                if all(i.state == 'posted' for i in rec.invoice_ids) and all(i.amount_residual == 0.00 for i in rec.invoice_ids):
                    rec.so_invoice_status = 'posted'
