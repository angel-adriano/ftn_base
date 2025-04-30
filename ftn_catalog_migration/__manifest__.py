# -*- coding: utf-8 -*-
{
    'name': 'Data Migration from Odoo 14 to Odoo 18',
    'version': '1.0',
    'summary': 'Module to migrate data from Odoo 14 to Odoo 18 via API',
    'description': 'Custom module to migrate products, variants, categories, and BoMs from Odoo 14.',

    'author': "FTNMX",
    'website': "http://www.formalizatunegocio.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Tools',
    'depends': ['base', 'product'],
    'data': [
        'security/data_migration_security.xml',
        'security/ir.model.access.csv',
        'views/data_migration_view.xml',
        'views/inherits.xml',
        'views/woocommerce.xml',
    ],
    'installable': True,
    'application': False,
}