# -*- coding: utf-8 -*-
{
    'name': "Sale Invoice Link",

    'summary': """
        This module is inteded to link invoices to Sales Order after a manual migration from one database to another""",

    'description': """
        Long description of module's purpose
    """,

    'author': "FTNMX",
    'website': "http://www.formalizatunegocio.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['sale', 'account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/inherits.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
