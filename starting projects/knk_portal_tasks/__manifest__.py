# -*- coding: utf-8 -*-

{
    'name': 'Create Tickets from Portal',
    'version': '14.0.0',
    'author': 'K&K IT',
    'website': 'http://knkit.sg',
    'currency': 'EUR',
    'depends': ['calendar', 'website_form'],
    'summary': "Allow your customers to create tasks on portal",
    'category': 'Productivity/Calendar',
    'data': [
        "security/helpdesk_security.xml",
        "security/ir.model.access.csv",
        "wizard/helpdesk_phonecall_to_phonecall_view.xml",
        'data/emails.xml',
        'data/ir_sequence_data.xml',
        'data/website_calendar_data.xml',
        'data/website_data.xml',
        'views/job_template.xml',
        'views/helpdesk_ticket.xml',
        'views/helpdesk_phonecall.xml',
        # 'views/res_partner.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'images': [
        'static/description/cover.png',
    ],
    'license': 'LGPL-3',
}
