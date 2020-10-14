# -*- coding: utf-8 -*-
{
    'name': "advanced_helpdesk",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mail', 'helpdesk', 'web','im_livechat'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/helpdesk_stage_inherit.xml',
        'views/im_livechat_form_ask_template.xml',
        'views/mail_channel_inherit.xml',
        'views/view_res_users_inherit.xml',
    ],
    'qweb': ['static/src/xml/*.xml'],
}
