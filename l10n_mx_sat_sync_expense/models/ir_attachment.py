# -*- coding: utf-8 -*-

from odoo import models, api, fields

class IrAttachment(models.Model):
    _inherit = 'ir.attachment'
    
    def _compute_hr_expense_count(self):
        for attach in self:
            attach.expense_count = len(attach.expense_ids)
            
    expense_ids = fields.Many2many("hr.expense",string="Expenses")
    expense_count = fields.Integer(compute='_compute_hr_expense_count', string='# de pagos')
    
    def action_view_expenses(self):
        expenses = self.mapped('expense_ids')
        action = self.env.ref('hr_expense.hr_expense_actions_my_unsubmitted').read()[0]
        
        if len(expenses) > 1:
            action['domain'] = [('id', 'in', expenses.ids)]
        elif len(expenses) == 1:
            action['views'] = [(self.env.ref('hr_expense.hr_expense_view_form').id, 'form')]
            action['res_id'] = expenses.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action