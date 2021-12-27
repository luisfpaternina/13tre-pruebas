# -*- coding: utf-8 -*-

from odoo.tests.common import TransactionCase
import datetime
from odoo.addons.bits_api_connect.models.api_connection\
    import ApiConnectionSoap, ApiConnectionRest


class BitsApiConnect(TransactionCase):

    def setUp(self):
        self.connection_soap = ApiConnectionSoap(
            'username_test',
            'password_test',
            'http://www.dneonline.com/calculator.asmx?wsdl',
        )
        self.connection_rest = ApiConnectionRest(
            'username_test',
            'password_test',
            'http://www.dneonline.com/calculator.asmx?wsdl',
        )

    def test_connection_to_api_soap(self):
        self.connection_soap.connect_to_api()

    def test_connection_to_api_rest(self):
        self.connection_rest.connect_to_api()
