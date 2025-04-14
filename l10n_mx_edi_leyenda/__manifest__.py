# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Complemento leyenda',
    'version': '16.01',
    'description': ''' 
                    Agrega campos en la compañía para colocar la información sobre el complemento leyenda.
                    En la factura se puede habilitar si se requiere que aparezca la factura con dicho complemento.
                    ''',
    'author': 'IT Admin',
    'website': 'www.itadmin.com.mx',
    'depends': ['l10n_mx_edi', 'l10n_mx_edi_40'],
    'data': [
        'data/4.0/cfdi.xml',

        'views/account_move_view.xml',
        'views/res_company_view.xml',
        'views/report_invoice.xml',
    ],
    'installable': True,
    'auto_install': False,
}
