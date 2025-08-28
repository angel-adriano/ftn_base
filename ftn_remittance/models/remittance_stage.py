from odoo import models, fields, api


class RemittanceStage(models.Model):
    _name = "remittance.stage"
    _description = 'Remittance Stage'

    name = fields.Char("Name", required=True, translate=True)
    sequence = fields.Integer("Sequence", default=20)
    fold = fields.Boolean("Folded in Remittance Pipe")
