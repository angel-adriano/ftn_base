# -*- coding: utf-8 -*-
{
    'name': 'Delivery and Invoice Status in Sale Order',
    'version': '14.0.1.0.0',
    'category': 'Sales',
    'summary': 'Show Delivery and Invoice Status in Sale Order, Filter Sale Orders based on Status, Sale Order Status',
    'description': """
        This module allows users to show the status of delivery orders and invoices for sale orders. Filters sale orders with partially delivered, delivered, partially paid, and paid. 
        Delivery order status in sale order, 
        Sales invoice status in sale order,
        Filter sale order with partially delivered order,
        Filter sale order with delivered order,
        Filter sale order with partially paid invoice,
        Filter sale order with paid invoice,
        Sale Order Status,
        Delivery and Invoice Status in Sale Order.
    """,
    'sequence': 1,
    'author': 'Futurelens',
    'website': 'http://thefuturelens.com',
    'depends': ['sale_management', 'stock', 'account'],
    'data': [
        'views/sale_order_view.xml',
        'views/assets.xml',
    ],
    'qweb': [],
    'css': [],
    'js': [],
    'images': [
        'static/description/banner_delivery_invoice_so_status.png',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'OPL-1',
    'price': 10,
    'currency': 'EUR',
    'live_test_url': 'https://youtu.be/ghGxLv4vFu0',
}
