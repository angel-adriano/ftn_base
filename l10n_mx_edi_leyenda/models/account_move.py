# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from lxml import etree
import logging
_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = 'account.move'

    leyenda = fields.Boolean(string='Leyenda', default=False,
        help="If this field is active, the CFDI that generates this invoice will include the complement "
             "'Leyenda'.")

    def _l10n_mx_edi_decode_cfdi(self, cfdi_data=None):
        # OVERRIDE

        def get_node(cfdi_node, attribute, namespaces):
            if hasattr(cfdi_node, 'Complemento'):
                node = cfdi_node.Complemento.xpath(attribute, namespaces=namespaces)
                return node[0] if node else None
            else:
                return None

        vals = super()._l10n_mx_edi_decode_cfdi(cfdi_data=cfdi_data)
        if vals.get('cfdi_node') is None:
            return vals

        if self.leyenda:
           cfdi_node = vals['cfdi_node']

           leyenda_node = get_node(
               cfdi_node,
               'leyendasFisc:LeyendasFiscales[1]',
               {'leyendasFisc': 'http://www.sat.gob.mx/leyendasFiscales'},
           ) or {}

           for char in leyenda_node.findall('{http://www.sat.gob.mx/leyendasFiscales}Leyenda'):
               vals.update({
                  'disposicionFiscal': char.get('disposicionFiscal', ''),
                  'norma': char.get('norma', ''),
                  'textoLeyenda': char.get('textoLeyenda', ''),
               })

        return vals

