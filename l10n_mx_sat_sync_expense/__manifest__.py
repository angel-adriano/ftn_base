# -*- coding: utf-8 -*-

{
    'name':         'Administrador de documentos Digitales Expense',
    'version': '    2.12',
    'description':  ''' 
                    
                    ''',
    'category':     'Expense',
    'author':       'IT Admin',
    'website':      '',
    'depends':      [
                    'l10n_mx_sat_sync_itadmin', 'hr_expense'
                    ],
    'data':         [
                    'views/ir_attachment_view.xml',
                    'wizard/xml_invoice_reconcile_view.xml',
                    ],
    'qweb':         [
                    
                    ],
    'application':  False,
    'installable':  True,
    'license':      'OPL-1',    
}
