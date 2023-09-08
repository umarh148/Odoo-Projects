# -*- coding: utf-8 -*-
{
    'name': "Assessment Module",
    'summary': """ """,
    'description': """ """,
    'author': "Umar",
    'sequence': -101,
    'category': 'Assessment',
    'version': '0.1',
    'depends': ['base', 'product', 'sale'],

    'data': [
        'security/ir.model.access.csv',
        'data/cart_sequence.xml',
        'views/menu.xml',
        'views/sale_agreement.xml',
        'views/create_quotation.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
