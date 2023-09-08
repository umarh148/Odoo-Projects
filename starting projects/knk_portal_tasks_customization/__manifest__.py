# -*- coding: utf-8 -*-
{
    'name': "Portal Customization",

    'summary': """
        Portal Customization""",

    'description': """
        Portal Customization
    """,

    'author': "K&K IT",
    'website': "https://knkit.sg",

    # for the full list
    'category': 'Project',
    'version': '1',

    # any module necessary for this one to work correctly
    'depends': ['base','mail','crm','helpdesk'],
    'data': [
        "views/users.xml",
    ]
}