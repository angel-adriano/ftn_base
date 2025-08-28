from odoo import models, fields, _
from odoo.exceptions import UserError


class AccountRemittanceGenerateWizard(models.TransientModel):
    _name = "account.remittance.generate.wizard"
    _description = "Generates remittance information"

    initial_date = fields.Datetime(string="Initial date")
    final_date = fields.Datetime(string="Final date")
    project_id = fields.Many2one(
        comodel_name="account.analytic.account", string="Project"
    )
    currency_id = fields.Many2one('res.currency', string="Moneda")
    type = fields.Selection([
        ('supplier', 'Proveedores'),
        ('expense', 'Gastos y reembolsos'),
        ('bonos', 'Bonos'),
    ], default="supplier", string='Tipo de Remesa')

    # Action buttons
    def action_generate_invoices(self):
        project_id = self.project_id.id
        final_date = self.final_date

        if project_id:
            domain = [
                ("move_type", "=", "in_invoice"),
                ("analytic_account_id", "=", project_id or False),
                ("next_due_date", "<=", final_date),
                ("state", "=", "posted"),
                ("next_due_amount", ">", 0.0),
                ("ready_to_pay", "=", True),
                ("currency_id", '=', self.currency_id.id),
            ]
        else:
            domain = [
                ("move_type", "=", "in_invoice"),
                ("next_due_date", "<=", final_date),
                ("state", "=", "posted"),
                ("next_due_amount", ">", 0.0),
                ("ready_to_pay", "=", True),
                ("currency_id", '=', self.currency_id.id),
            ]

        invoices = self.env["account.move"].search(domain)
        if not invoices:
            raise UserError(_("There are no invoices to pay"))

        # Create new remittance
        remittance = self.env["account.remittance"].create({
            "initial_date": self.initial_date,
            "final_date": self.final_date,
            "project_id": self.project_id.id,
            "currency_id": self.currency_id.id,
            "stage_id": self.env.ref("ftn_remittance.stage_0").id,
            "approver_id": self.project_id.approver_id.id if self.project_id.approver_id else self.env.user.id,
            "responsible_id": self.env.user.id,
        })

        for invoice in invoices:
            self.env["account.remittance.line"].create({
                "invoice_id": invoice.id,
                "name": invoice.name,
                "partner_id": invoice.partner_id.id,
                "amount_total": invoice.amount_total,
                "amount_residual": invoice.amount_residual,
                "amount_to_pay": invoice.next_due_amount,
                "remittance_id": remittance.id,
            })

        return {
            "type": "ir.actions.act_window",
            "res_model": "account.remittance",
            "res_id": remittance.id,
            "view_mode": "form",
            "target": "current",
        }
