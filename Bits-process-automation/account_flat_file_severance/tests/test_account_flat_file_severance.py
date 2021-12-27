from datetime import date
from odoo.tests.common import TransactionCase


class TestAccountFlatFileSeverance(TransactionCase):

    def setUp(self):
        super(TestAccountFlatFileSeverance, self).setUp()

        self.FlatFile = self.env['account.flat.file.base']
        # self.HrPayslip = self.env['hr.payslip']
        self.HrEmployee = self.env['hr.employee']
        self.HrContract = self.env['hr.contract']
        self.HrPayrollStructureType = self.env['hr.payroll.structure.type']
        self.HrPayrollStructure = self.env['hr.payroll.structure']
        # self.HrPayslipWorkedDays = self.env['hr.payslip.worked_days']

        self.AccountPayment = self.env['account.payment']
        self.AccountJournal = self.env['account.journal']
        self.AccountAccount = self.env['account.account']
        self.AccountMove = self.env['account.move']
        self.Respartner = self.env['res.partner']
        self.ResPartnerBank = self.env['res.partner.bank']
        self.ResCompany = self.env['res.company'].search([])
        self.ResBank = self.env['res.bank']
        self.AccountAnalyticAccount = self.env['account.analytic.account']

        self.account_payroll = self.AccountJournal.create({
            'name': 'Nomina',
            'code': 'NOM',
            'type': 'general'
        })

        self.account_bank = self.AccountAccount.create({
            'code': "10151206",
            'name': "TEST Account Bank",
            'user_type_id': self.env.ref(
                'account.data_account_type_liquidity').id
        })

        self.center_cost = self.AccountAnalyticAccount.create({
            'name': 'Desarrollo',
            'code': 'dev'
        })

        self.res_partner = self.Respartner.create({
            'name': "Test Partner"
        })

        self.res_partner_2 = self.Respartner.create({
            'name': 'Test'
        })

        self.payroll_structure_type = self.HrPayrollStructureType.create({
            'name': 'Structure type test',
            'wage_type': 'monthly',
            # 'is_novelty': True
        })

        self.payroll_structure = self.HrPayrollStructure.create({
            'name': 'Structures Test',
            'type_id': self.payroll_structure_type.id
        })

        self.contract = self.HrContract.create({
            'name': 'contract example',
            'date_start': date(2020, 1, 1),
            'wage': 2800000,
            'structure_type_id': self.payroll_structure_type.id
        })

        self.employee = self.HrEmployee.create({
            'name': 'Employee Test',
            'names': 'Employee full name',
            'surnames': 'Employee surnames',
            'known_as': 'Employee Known',
            'document_type': '13',
            'identification_id': "78945612",
            'contract_id': self.contract.id,
        })

        # self.hr_payslip = self.HrPayslip.create({
        #     'name': 'Paylisp Test',
        #     'employee_id': self.employee.id,
        #     'contract_id': self.contract.id,
        #     'struct_id': self.payroll_structure.id,
        #     'date_from': date(2020, 3, 1),
        #     'date_to': date(2020, 3, 31),
        #     'move_id': self.account_move.id,
        #     'general_state': 'approved'
        # })

        # self.work_entry_type = self.env['hr.work.entry.type'].search([
        #     ('code', '=', 'WORK100')
        # ], limit=1)

        # self.worked_days = self.HrPayslipWorkedDays.create({
        #     'work_entry_type_id': self.work_entry_type.id,
        #     'sequence': 25,
        #     'number_of_hours': 184.00,
        #     'name': self.work_entry_type.name,
        #     'number_of_days': 30.00,
        #     'contract_id': self.contract.id,
        #     'amount': self.contract.wage,
        #     'payslip_id': self.hr_payslip.id
        # })

        self.res_bank = self.ResBank.create({
            'name': "Test Res Bank",
            'bic': "5"
        })

        self.res_partner_bank = self.ResPartnerBank.create({
            'bank_id': self.res_bank.id,
            'partner_id': self.ResCompany.partner_id.id,
            'acc_number': "159753456"
        })

        self.journal_bank = self.AccountJournal.create({
            "name": "Test Bank",
            "code": "TESB",
            "type": "bank",
            'default_credit_account_id': self.account_bank.id,
            'default_debit_account_id':  self.account_bank.id,
            'bank_account_id': self.res_partner_bank.id
        })

        self.account_payment = self.AccountPayment.create({
            'journal_id': self.journal_bank.id,
            'payment_type': "outbound",
            'partner_type': "supplier",
            'amount': 2000,
            'payment_date': date(2020, 5, 30),
            'partner_id': self.res_partner.id,
            'payment_method_id': self.env.ref(
                'account.account_payment_method_manual_out').id
        })

        self.account_payment_2 = self.AccountPayment.create({
            'journal_id': self.journal_bank.id,
            'payment_type': "outbound",
            'partner_type': "supplier",
            'amount': 2000,
            'payment_date': date(2020, 5, 30),
            'partner_id': self.res_partner_2.id,
            'payment_method_id': self.env.ref(
                'account.account_payment_method_manual_out').id
        })

        self.account_move = self.AccountMove.create({
            'name': 'NOM/2020/0002',
            'ref': 'Month 2020',
            'date': date(2020, 3, 31),
            'journal_id': self.account_payroll.id,
            'line_ids': [
                (0, 0, {
                    'name': 'PROVISION INTERESES CESANTIAS',
                    'partner_id': self.res_partner.id,
                    'account_id': self.account_bank.id,
                    'journal_id': self.account_payroll.id,
                    'date': date(2020, 3, 31),
                    'credit': 56000,
                    'debit': 0.0,
                    'analytic_account_id': self.center_cost.id,
                    'payment_id': self.account_payment.id
                }),
                (0, 0, {
                    'name': 'PROVISION INTERESES CESANTIAS',
                    'partner_id': self.res_partner.id,
                    'account_id': self.account_bank.id,
                    'journal_id': self.account_payroll.id,
                    'date': date(2020, 3, 31),
                    'debit': 56000,
                    'credit': 0,
                    'analytic_account_id': self.center_cost.id,
                    'payment_id': self.account_payment.id
                })
            ]
        })

        self.account_move_2 = self.AccountMove.create({
            'name': 'NOM/2020/0002',
            'ref': 'Month 2020',
            'date': date(2020, 3, 31),
            'journal_id': self.account_payroll.id,
            'line_ids': [
                (0, 0, {
                    'name': 'PROVISION INTERESES CESANTIAS',
                    'partner_id': self.res_partner_2.id,
                    'account_id': self.account_bank.id,
                    'journal_id': self.account_payroll.id,
                    'date': date(2020, 3, 31),
                    'debit': 0.0,
                    'credit': 56000,
                    'analytic_account_id': self.center_cost.id,
                    'payment_id': self.account_payment_2.id
                }),
                (0, 0, {
                    'name': 'PROVISION INTERESES CESANTIAS',
                    'partner_id': self.res_partner_2.id,
                    'account_id': self.account_bank.id,
                    'journal_id': self.account_payroll.id,
                    'date': date(2020, 3, 31),
                    'debit': 56000,
                    'credit': 0,
                    'analytic_account_id': self.center_cost.id,
                    'payment_id': self.account_payment_2.id
                })
            ]
        })

    def test_generate_csv(self):
        record = self.FlatFile.new({
            'partner_id': self.account_payment.partner_id.id,
            'payment_description': "DEMO001",
            'file_type': 'get_collect_data_payoffs',
            'transaction_type': 'electronic_transaction',
            'application_date': '2020-05-01',
        })

        ctx = {
            'payment_name': self.account_payment.name,
            'active_model': 'account.payment',
            'active_id': self.account_payment.id,
        }

        record.with_context(ctx).get_collect_data()

    # def test_whitout_move_line(self):
    #     record = self.FlatFile.new({
    #         'partner_id': self.account_payment_2.partner_id.id,
    #         'payment_description': "DEMO002",
    #         'file_type': 'get_collect_data_payoffs',
    #         'transaction_type': 'electronic_transaction',
    #         'application_date': '2020-05-01',
    #     })
    #     record.get_collect_data()

    def test_unselect_layoffs(self):
        record = self.FlatFile.new({
            'partner_id': self.account_payment_2.partner_id.id,
            'payment_description': "DEMO003",
            'file_type': 'get_collect_data_bank',
            'transaction_type': 'electronic_transaction',
            'application_date': '2020-05-01',
        })

        ctx = {
            'payment_name': self.account_payment_2.name,
            'active_model': 'account.payment',
            'active_id': self.account_payment_2.id,
        }

        record.with_context(ctx).get_collect_data()
