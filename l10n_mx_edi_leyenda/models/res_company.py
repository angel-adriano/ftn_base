# -*- coding: utf-8 -*-
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    disposicionfiscal = fields.Char(string='Disposición fiscal')
    norma= fields.Char(string='Norma')
    textoleyenda = fields.Char(string='Texto leyenda')
