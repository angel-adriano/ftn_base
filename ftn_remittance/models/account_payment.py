from odoo import models, fields


class AccountPayment(models.Model):
    _inherit = "account.payment"

    remittance_id = fields.Many2one(
        comodel_name="account.remittance",
        string="Remittance",
        index=True,
        ondelete="set null",
    )

