from odoo import fields, models, api


class AcountAnalytic(models.Model):
    _inherit = 'account.analytic.account'

    approver_id = fields.Many2one(
        comodel_name="res.users", string="Approver", tracking=True, domain=[('share', '=', False)]
    )
