from odoo import models, api, fields


class Company(models.Model):
    _inherit = 'res.company'

    active = fields.Boolean(default=True)
