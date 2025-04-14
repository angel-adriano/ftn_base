# -*- coding: utf-8 -*-
from odoo import models, fields


class AccountEdiFormat(models.Model):
    _inherit = 'account.edi.format'

    def _l10n_mx_edi_get_invoice_cfdi_values(self, invoice):
        # OVERRIDE
        vals = super()._l10n_mx_edi_get_invoice_cfdi_values(invoice)

        if invoice.leyenda:

            vals.update({
                'disposicionfiscal': invoice.company_id.disposicionfiscal,
                'norma': invoice.company_id.norma,
                'textoleyenda': invoice.company_id.textoleyenda,
            })

        return vals
