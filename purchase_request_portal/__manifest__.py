# Copyright 2026
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

{
    'name': 'Purchase Request Portal',
    'version': '19.0.1.0.0',
    'category': 'Purchase Management',
    'summary': 'Web portal for employees to submit purchase requests without user registration',
    'author': 'FTNMX',
    'website': 'https://www.formalizatunegoio.com',
    'license': 'LGPL-3',
    'depends': [
        'purchase_request',
        'hr',
        'portal',
        'web',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/config_data.xml',
        'views/purchase_request_views.xml',
        'views/purchase_request_portal_templates.xml',
        'views/res_config_settings_views.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'purchase_request_portal/static/src/css/portal.css',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}
