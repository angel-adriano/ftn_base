# -*- coding: utf-8 -*-
{
    'name': "Purchase Services Receive",

    'summary': """
        Allow to use a wizard to receive services or manual items in Purchase Orders""",

    'description': """
        Depends on Cybrosys module "Delivery Status on Purchase Order" which can be downloaded from Odoo App Store: https://apps.odoo.com/apps/modules/16.0/purchase_order_delivery_status
    """,

    'author': "FTNMX",
    'website': "http://www.formalizatunegocio.com.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'i18n': ['i18n/es_MX.po'],
    'category': 'Administration',
    'version': '16.0',
    'application': True,
    'price': 19.99,
    'currency': 'USD',

    # any module necessary for this one to work correctly
    'depends': ['purchase', 'purchase_order_delivery_status'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        # 'views/views.xml',
        'views/inherits.xml',
        'wizard/purchase_order.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
