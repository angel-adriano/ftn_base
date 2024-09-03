# -*- coding: utf-8 -*-
from odoo import models,fields,api
import base64
#from lxml import etree
import json, xmltodict
#from .cfdi_invoice import convert_to_special_dict

#from .special_dict import CaselessDictionary
#from ...l10n_mx_sat_sync_itadmin.models.special_dict import CaselessDictionary
from odoo.addons.l10n_mx_sat_sync_itadmin.models.special_dict import CaselessDictionary

def convert_to_special_dict(d):
    for k, v in d.items():
        if isinstance(v, dict):
            d.__setitem__(k, convert_to_special_dict(CaselessDictionary(v)))
        else:
            d.__setitem__(k, v)
    return d

import logging
_logger = logging.getLogger(__name__)

class ReconcileVendorCfdiXmlBill(models.TransientModel):
    _inherit ='reconcile.vendor.cfdi.xml.bill'
    
    typo_de_combante = fields.Selection(selection_add=[('Gastos', 'Gastos')])
    
    def action_reconcile(self):
        if self.typo_de_combante!='Gastos':
            return super(ReconcileVendorCfdiXmlBill, self).action_reconcile()
        
        selected_att_ids = self._context.get('active_ids')
        if not selected_att_ids or self._context.get('active_model','')!='ir.attachment':
            return
        
        attachments = self.env['ir.attachment'].search([('id','in', selected_att_ids), ('creado_en_odoo','!=',True)]) #, ('cfdi_type','=', self.typo_de_combante)
        
        expense_obj = self.env['hr.expense']
        reconcile_obj = self.env['xml.invoice.reconcile']
        
        created_ids = []
        for attachment in attachments:
            file_content = base64.b64decode(attachment.datas)
            if b'xmlns:schemaLocation' in file_content:
                file_content = file_content.replace(b'xmlns:schemaLocation', b'xsi:schemaLocation')
            file_content = file_content.replace(b'cfdi:',b'')
            file_content = file_content.replace(b'tfd:',b'')
            try:
                data = json.dumps(xmltodict.parse(file_content)) #,force_list=('Concepto','Traslado',)
                data = json.loads(data)
            except Exception as e:
                data = {}
                raise Warning(str(e))
            
            data = CaselessDictionary(data)
            data = convert_to_special_dict(data)
            
            date_invoice = data.get('Comprobante',{}).get('@Fecha')
            Complemento = data.get('Comprobante',{}).get('Complemento',{})
            
            total = eval(data.get('Comprobante',{}).get('@Total','0.0'))
                
            cust_data = data.get('Comprobante',{}).get('Emisor',{})
            uso_data = data.get('Comprobante',{}).get('Receptor',{})
            client_rfc = cust_data.get('@rfc')
            client_name = cust_data.get('@nombre')
            
            timbrado_data = Complemento.get('TimbreFiscalDigital',{})
            
            vals = {
                'client_name' : client_name,
                'date' : date_invoice, #tree_attrib_dict.get('fecha'),
                'amount' : total,
                'attachment_id' : attachment.id,
                'tipo_comprobante': data.get('Comprobante',{}).get('@TipoDeComprobante',{}),
                'folio_fiscal':timbrado_data.get('@UUID'),
                'forma_pago':data.get('Comprobante',{}).get('@FormaPago',''),
                'methodo_pago':data.get('Comprobante',{}).get('@MetodoPago',''),
                'uso_cfdi':uso_data.get('@UsoCFDI'),
                'numero_cetificado': timbrado_data.get('@NoCertificadoSAT'),
                'fecha_certificacion': timbrado_data.get('@FechaTimbrado'),
                'selo_digital_cdfi': timbrado_data.get('@SelloCFD'),
                'selo_sat': timbrado_data.get('@SelloSAT'),
                'tipocambio': data.get('Comprobante',{}).get('@TipoCambio'),
                'moneda': data.get('Comprobante',{}).get('@Moneda'),
                'folio_factura': data.get('Comprobante',{}).get('@Folio'),
                }
            
            expenses_exist = expense_obj.search([('total_amount','=',total)])
            if expenses_exist:
                expenses_exist
                expense_ids = attachment.expense_ids.ids
                
                not_attached_expenses = expenses_exist.filtered(lambda x: x.id not in expense_ids)
                if not_attached_expenses:
                    vals.update({'expense_id':not_attached_expenses[0].id})
                else:
                    expense_exist = expenses_exist.filtered(lambda x:x.state in ['draft','reported'])
                    if expense_exist:
                        vals.update({'expense_id':expense_exist[0].id})
                    else:
                        vals.update({'expense_id':expenses_exist[0].id})
                        
            record = reconcile_obj.create(vals)
            created_ids.append(record.id)
        
        action_id = 'l10n_mx_sat_sync_expense.action_xml_hr_expanese_reconcile_view'
        action = self.env.ref(action_id).read()[0]
        action['domain'] = [('id', 'in', created_ids)]
        action['context'] = {'typo_de_combante': self.typo_de_combante}
        return action
    
    