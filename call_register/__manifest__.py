# -*- coding: utf-8 -*-

{
    'name': "Registro de llamadas RingOver",
    'summary': """
        Registro de llamadas RingOver
    """,
    'description': """
        Registro de llamadas RingOver
    """,
    'author': "JUMO Technologies",
    'website': "",
    'category': 'Tools',
    'version': '1.4',
    'depends': ['contacts', 'web'],
    'license': 'GPL-3',
    'images': ['static/description/icon.png'],
    'data': [
        # Security
        'security/call_security.xml',
        'security/ir.model.access.csv',
        # Data
        'data/call_ir_cron_data.xml',
        # Views
        'views/assets.xml',
        'views/dashboard_views.xml',
        'views/call_register_view.xml',
        'views/res_config_settings.xml',
        'views/res_users_view.xml',
        # Wizard
        'wizard/synchronization_calls_wzd.xml'
    ],
    # 'assets': {
    #     'web.assets_backend': [
    #             'call_register/static/src/scss/style.scss',
    #             'call_register/static/src/lib/bootstrap-toggle-master/css/bootstrap-toggle.min.css',
    #             'call_register/static/src/lib/Chart.bundle.min.js',
    #             'call_register/static/src/lib/Chart.min.js',
    #             'call_register/static/src/lib/bootstrap-toggle-master/js/bootstrap-toggle.min.js',
    #             'call_register/static/src/js/call_dashboard.js',                
    #         ],
    #     'web.assets_qweb': [
    #         'call_register/static/src/xml/call_dashboard.xml',
    #     ],
    # },
    'qweb': [
        'static/src/xml/call_dashboard.xml'
    ],
}
