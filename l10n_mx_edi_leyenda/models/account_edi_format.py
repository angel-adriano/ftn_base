# -*- coding: utf-8 -*-
from odoo import models, fields


class AccountEdiFormat(models.Model):
    _inherit = 'account.edi.format'

    def _l10n_mx_edi_get_invoice_cfdi_values(self, invoice):
        # OVERRIDE
        vals = super()._l10n_mx_edi_get_invoice_cfdi_values(invoice)

        if invoice.leyenda:

            vals.update({
                'disposicionfiscal': invoice.partner_id.x_studio_disposicion_fiscal,
                'norma': invoice.partner_id.x_studio_norma,
                'textoleyenda': invoice.partner_id.x_studio_texto_leyenda,
            })

        return vals
