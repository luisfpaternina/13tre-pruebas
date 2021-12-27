from datetime import datetime, date
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestHrContract(TransactionCase):

    def setUp(self):
        super(TestHrContract, self).setUp()
        self.ref_history = self.env['hr.contract.history']
        self.ref_contract = self.env['hr.contract']

        self.contract = self.ref_contract.create({
            'name': 'Peterson Contract',
            'wage': 1000000
        })

    def test_create_contract(self):
        record = self.ref_contract.create({
            'name': 'Peterson Contract 2',
            'wage': 1000000
        })
        record.write({
            'name': 'Peterson Contract2',
        })

    def test_write_contract(self):
        self.contract.write({
            'wage': 2000000
        })
        history = self.ref_history.search([
            ('contract_id', '=', self.contract.id)])
        self.assertEqual(len(history), 2)
