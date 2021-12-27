# -*- coding: utf-8 -*-

from odoo.tests.common import TransactionCase


class TestTechProvider(TransactionCase):

    def setUp(self):
        super(TestTechProvider, self).setUp()
        self.tech_provider = self.env['l10n_co.tech.provider']
        self.tech_provider_1 = self.tech_provider.create({
            'name': 'Provedor tecnologico prueba',
            'code': 'PTP434',
            'description': 'Descripcion provedor tecnologico de prueba',
            'username': 'uriel234d',
            'password': 'Qazxer5645@|',
            'file_extension': 'txt',
            'file_separator': '|',
            'file_filename': 'Nombre de prueba',
            'num_doc_attachs': 10,
        })

    def test_collect_data_tech_provider(self):
        self.tech_provider_1.get_collect_data()

    def test_get_data_file_tech_provider(self):
        self.tech_provider_1.get_data_file()

    def test_connection_test(self):
        self.tech_provider_1.action_test_connection()
