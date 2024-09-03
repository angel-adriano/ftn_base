# -*- coding: utf-8 -*-

from odoo import models,api, fields
from odoo.exceptions import Warning

class XMLInvoiceReconcile(models.TransientModel):
    _inherit = 'xml.invoice.reconcile'
    
    expense_id = fields.Many2one('hr.expense',"Expense")
    
    def action_reconcile(self):
        ctx = self._context.copy()
        if ctx.get('typo_de_combante','')!='Gastos':
            return super(XMLInvoiceReconcile, self).action_reconcile()
        self.ensure_one()
        expense = self.expense_id
        if not expense:
            raise Warning("Seleccionar primero la factura/pago y posteriormente reconciliar con el XML.")
        
        self.attachment_id.write({'creado_en_odoo':True, 'res_id': expense.id, 'res_model': expense._name,'expense_ids':[(4,expense.id)]})
        self.write({'reconcilled':True})
        
        return 