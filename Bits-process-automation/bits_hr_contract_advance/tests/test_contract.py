from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestHrContract(TransactionCase):

    def setUp(self):
        super(TestHrContract, self).setUp()
        self.HrContract = self.env['hr.contract']
        self.HrSalaryAid = self.env['hr.salary.aid']
        self.HrContractSalaryAid = self.env['hr.contract.salary.aid']

        self.contractEmployee = self.HrContract.create({
            'name': 'Abigail Peterson Contract',
            'structure_type_id': 1,
            'wage': 1000000
        })

        self.hrSalaryAid1 = self.HrContractSalaryAid.create({
            'value': 1000,
            'contract_id': self.contractEmployee.id,
            'salary_aid_id': 1
        })

        self.hrSalaryAid2 = self.HrContractSalaryAid.create({
            'value': 2000,
            'contract_id': self.contractEmployee.id,
            'salary_aid_id': 2
        })

    def test_search_salary_aid_success(self):
        if self.contractEmployee:
            food_salary_aid = self.contractEmployee.searchSalaryAid('237')
            parking_salary_aid = self.contractEmployee.searchSalaryAid('238')
            road_salary_aid = self.contractEmployee.searchSalaryAid('239')

    def test_validate_fields(self):
        with self.assertRaises(ValidationError):
            self.HrContract.create({
                'name': 'Abigail Peterson Contract',
            })

    def test_validate_fields_success(self):
        self.HrContract.create({
            'name': 'Abigail Peterson Contract',
            'structure_type_id': 1,
            'wage': 1000000
        })
