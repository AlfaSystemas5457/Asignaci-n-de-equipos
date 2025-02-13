# -*- coding: utf-8 -*-
{
    'name': 'Asignación de equipos',
    'version': '18.0.1.5',
    'sequence': 1,
    'author': 'DGV',
    'website': 'https://github.com/AlfaSystemas5457/dev_equipment_allocation',
    'category': 'Human Resources',
    'description':"""Modulo de asignación de equipos""",
    'summary': 'Modulo de asignación de equipos',
    'license': 'LGPL-3',
    'depends': ['maintenance', 'mail', 'hr'],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/sequence_allocation.xml',
        'data/sequence_replace.xml',
        'data/allocated_email_template.xml',
        'data/submitted_email_template.xml',
        'data/rejected_email_template.xml',
        'data/reminder_email_template.xml',
        'data/cron_return_reminder.xml',
        'data/report_paperformat.xml',
        'views/format_reports_layout.xml',
        'views/res_config_settings.xml',
        'wizard/reject_reason.xml',
        'wizard/replace_equipment.xml',
        'views/equipment.xml',
        'views/equipment_allocation.xml',
        'views/equipment_replacement.xml',
        'views/report_template_id.xml',
        'views/departament_details.xml',
    ],
    # 'assets': {
    #     'web.assets_backend':[
    #         'dev_equipment_allocation/static/src/css/reposrt.css'
    #     ]
    # },
    'installable': True,
    'application': True,
    'auto_install': False,
}
