# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Credit Limit Checker',
    'version': '1',
    'website': 'https://www.subtletechs.com/',
    'author': 'Subtle Technologies (Pvt) Ltd',
    'depends': [
        'base',
        'sale',
    ],
    'data': [
        'views/res_partner_view.xml',
    ],

    'installable': True,
    'application': True,
}
