import odoo.tests

from datetime import date
from datetime import datetime, timedelta

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError
from odoo import fields, models, tools
from odoo.modules.module import get_module_resource


class TestAccountFlatFileParafiscal(TransactionCase):

    def setUp(self):
        super(TestAccountFlatFileParafiscal, self).setUp()

        self.AccountJournal = self.env['account.journal']
        self.AccountAccount = self.env['account.account']
        self.ResBank = self.env['res.bank']
        self.Respartner = self.env['res.partner']
        self.ResPartnerBank = self.env['res.partner.bank']
        self.AccountPayment = self.env['account.payment']
        self.AccountAnalytic = self.env['account.analytic.account']
        self.FlatFile = self.env['account.flat.file.base']
        self.ResCompany = self.env['res.company'].search([])
        self.wizard_payment = self.env['account.collective.payments.wizard']

        self.env['ir.config_parameter'].sudo().set_param(
            'percentage_workload', float(100))

        self.env['ir.config_parameter'].sudo().set_param(
            'hr_payroll.integrate_payroll_news', True)

        test_country = self.env['res.country'].create({
            'name': "L'Île de la Mouche",
            'code': 'YY',
        })

        test_state = self.env['res.country.state'].create(dict(
            name="State",
            code="ST",
            l10n_co_divipola="0001",
            country_id=test_country.id))

        town = self.env['res.country.town'].create(dict(
            name="town",
            code="TW",
            l10n_co_divipola="0011",
            state_id=test_state.id,
            country_id=test_country.id))

        self.contact = self.Respartner.create({
            'name': 'partner name',
            'town_id': town.id
        })

        self.ir_sequence = self.env['ir.sequence'].create({
            'name': 'SEQ',
            'padding': 4,
            'number_increment': 1,
        })

        self.account_journal = self.AccountJournal.create({
            'name': 'MISC',
            'code': 'MSC',
            'type': 'general',
            'sequence_id': self.ir_sequence.id,
        })

        self.account_bank = self.AccountAccount.create({
            'code': "10151206",
            'name': "TEST Account Bank",
            'user_type_id': self.env.ref(
                'account.data_account_type_liquidity').id
        })
        self.account_payable = self.AccountAccount.create({
            'code': "23151206",
            'name': "TEST Account Payable",
            'user_type_id': self.env.ref(
                'account.data_account_type_payable').id,
            'reconcile': True
        })
        self.account_receivable = self.AccountAccount.create({
            'code': "21151206",
            'name': "TEST Account Payable",
            'user_type_id': self.env.ref(
                'account.data_account_type_receivable').id,
            'reconcile': True
        })
        self.res_partner = self.Respartner.create({
            'name': "Test Partner",
            'property_account_payable_id': self.account_payable.id,
            'property_account_receivable_id': self.account_receivable.id
        })
        self.res_bank = self.ResBank.create({
            'name': "Test Res Bank",
            'bic': "5"
        })
        self.res_partner_bank = self.ResPartnerBank.create({
            'bank_id': self.res_bank.id,
            'partner_id': self.ResCompany.partner_id.id,
            'acc_number': "159753456"
        })
        self.journal_bank = self.env['account.journal'].create({
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

        self.hr_contract = self.env['hr.contract']
        self.hr_payslip = self.env['hr.payslip']
        self.hr_employee = self.env['hr.employee']
        self.hr_salary_rule = self.env['hr.salary.rule']
        self.hr_salary_rule_category = self.env['hr.salary.rule.category']
        self.hr_payroll_structure = self.env['hr.payroll.structure']
        self.hr_payroll_structure_type = self.env['hr.payroll.structure.type']
        self.hr_payroll_news = self.env['hr.payroll.news']

        self.payable_type_id = self.env.ref(
            'account.data_account_type_payable')

        self.salary_rule_category = self.hr_salary_rule_category.create({
            'name': "Salary Category Test",
            'code': "SCT"
        })

        self.structure_type = self.hr_payroll_structure_type.create({
            'name': "Test Type",
            'wage_type': "monthly"
        })

        self.contract = self.hr_contract.create({
            'name': "Contract Test",
            'date_start': datetime.now(),
            'date_end': datetime.now()+timedelta(days=365),
            'wage': 3150000,
            'structure_type_id': self.structure_type.id
        })

        self.contract_001 = self.hr_contract.create({
            'name': "Contract 001",
            'date_start': datetime.now(),
            'date_end': datetime.now()+timedelta(days=365),
            'wage': 3150000,
            'structure_type_id': self.structure_type.id
        })

        self.account_analytic = self.AccountAnalytic.create({
            'name': 'TEST',
            'code': '0001'
        })

        self.employee = self.hr_employee.create({
            'name': "Test Payroll News",
            'contract_id': self.contract.id,
            'document_type': '13',
            'identification_id': "75395146",
            'names': 'NOMBRE1 NOMBRE2',
            'surnames': 'APELLIDO1 APELLIDO2',
            'known_as': 'SuperCode',
            'address_home_id': self.contact.id,
            'employee_center_cost_ids': [(0, 0, {
                'percentage': 100.00,
                'account_analytic_id': self.account_analytic.id
            })]
        })

        self.employee_001 = self.hr_employee.create({
            'name': "Empoyee 001",
            'contract_id': self.contract_001.id,
            'document_type': '13',
            'identification_id': "75334146",
            'names': 'NOMBRE1 NOMBRE2',
            'surnames': 'APELLIDO1 APELLIDO2',
            'known_as': 'SuperCode',
            'address_home_id': self.contact.id,
            'employee_center_cost_ids': [(0, 0, {
                'percentage': 100.00,
                'account_analytic_id': self.account_analytic.id
            })]
        })

        self.payroll_structure = self.hr_payroll_structure.create({
            'name': "Structure Test",
            'type_id': self.structure_type.id,
            'journal_id': self.account_journal.id,
        })

        self.payroll_structure_2 = self.hr_payroll_structure.create({
            'name': "Structure Test 2",
            'type_id': self.structure_type.id,
            'journal_id': self.account_journal.id,
        })

        self.salary_rule_02 = self.hr_salary_rule.create({
            'name': "TEST IBC",
            'code': "3023",
            'sequence': 100,
            'struct_id': self.payroll_structure_2.id,
            'category_id': self.salary_rule_category.id,
            'condition_select': "none",
            'amount_select': "fix",
            'amount_fix': 3000,
            'quantity': 30,
            "account_debit": self.account_payable.id,
            "account_credit": self.account_payable.id,
        })

        self.salary_rule_01 = self.hr_salary_rule.create({
            'name': "TEST RULE NOVELTY",
            'code': "002",
            'sequence': 100,
            'struct_id': self.payroll_structure_2.id,
            'category_id': self.salary_rule_category.id,
            'condition_select': "none",
            'amount_select': "fix",
            'amount_fix': 3000,
            'quantity': 30,
            "account_debit": self.account_payable.id,
            "account_credit": self.account_payable.id,
        })

        self.salary_rule = self.hr_salary_rule.create({
            'name': "ITEM PARAFISCAL",
            'code': "001",
            'sequence': 50,
            'struct_id': self.payroll_structure.id,
            'category_id': self.salary_rule_category.id,
            'condition_select': "none",
            'amount_select': "fix",
            'amount_fix': 3000,
            'quantity': 1.0,
            "account_debit": self.account_payable.id,
            "account_credit": self.account_payable.id,
        })

        self.payslip = self.hr_payslip.create({
            'name': "Payroll Test",
            'employee_id': self.employee.id,
            'contract_id': self.contract.id,
            'journal_id': self.account_journal.id,
            'struct_id': self.payroll_structure.id,
            'general_state': 'approved',
            'date_from': datetime.now(),
            'date_to': datetime.now()+timedelta(days=365)
        })

        self.payslip_without_novelties = self.hr_payslip.create({
            'name': "Payroll Test",
            'employee_id': self.employee_001.id,
            'contract_id': self.contract_001.id,
            'journal_id': self.account_journal.id,
            'struct_id': self.payroll_structure.id,
            'general_state': 'approved',
            'date_from': datetime.now() + timedelta(days=1),
            'date_to': datetime.now()+timedelta(days=365)
        })

        self.stage_id = self.env['hr.payroll.news.stage'].search(
            [('is_approved', '=', True)])

        self.novelty_1 = self.hr_payroll_news.create({
            'name': 'Novelty Tests',
            'payroll_structure_id': self.payroll_structure_2.id,
            'salary_rule_id': self.salary_rule_02.id,
            'date_start': datetime.now(),
            'date_end': datetime.now(),
            'request_date_from': datetime.now(),
            'request_date_to': datetime.now() + timedelta(days=5),
            'kanban_state': 'done',
            'stage_id': self.stage_id.id,
            'employee_payroll_news_ids': [(0, 0, {
                'employee_id': self.employee.id,
                'quantity': 20,
                'amount': 100
            })]
        })

        self.novelty = self.hr_payroll_news.create({
            'name': 'Novelty Tests',
            'payroll_structure_id': self.payroll_structure_2.id,
            'salary_rule_id': self.salary_rule_01.id,
            'date_start': datetime.now(),
            'date_end': datetime.now(),
            'request_date_from': datetime.now(),
            'request_date_to': datetime.now() + timedelta(days=5),
            'kanban_state': 'done',
            'stage_id': self.stage_id.id,
            'employee_payroll_news_ids': [(0, 0, {
                'employee_id': self.employee.id,
                'quantity': 20,
                'amount': 100
            })]
        })

        self.payroll_new = self.env['hr.payroll.news'].create({
            'name': "Test Novelty",
            'payroll_structure_id': self.payroll_structure.id,
            'salary_rule_id': self.salary_rule.id,
            'kanban_state': "done",
            'date_start': datetime.now(),
            'date_end': datetime.now() + timedelta(days=5),
            'request_date_from': datetime.strptime(
                '2020-12-20', '%Y-%m-%d'
            ),
            'request_date_to': datetime.strptime(
                '2020-12-22', '%Y-%m-%d'
            ),
            'stage_id': self.stage_id.id,
            'employee_payroll_news_ids': [(0, 0, {
                'employee_id': self.employee.id,
                'quantity': 1,
                'amount': 100
            })]
        })

        self.termination = self.ref(
            'hr_payroll_settlement.reason_dsjc_nor')

        self.settlement = self.env['settlement.history'].create({
            'employee_id': self.employee.id,
            'contract_id': self.contract.id,
            'date_payment': datetime.now(),
            'reason_for_termination': self.termination,
            'compensation': False,
        })

    def test_without_setting_rules_get_collect_data_parafiscal(self):
        record = self.FlatFile.new({
            'partner_id': self.account_payment.partner_id.id,
            'payment_description': "DEMO001",
            'file_type': 'get_collect_data_parafiscal',
            'template_modality': '1',
            'transaction_type': 'electronic_transaction',
            'template_type': 'E',
            'application_date': '2020-05-01',
        })

        self.payslip_without_novelties.compute_sheet()
        self.payslip_without_novelties.action_payslip_done()

        lines = self.env['account.move.line'].search([
            ('account_id.user_type_id', '=', self.payable_type_id.id)])
        wizard_payment = self.wizard_payment.new({
            'journal_id': self.journal_bank.id,
            'date_from_f': '2020-05-01',
            'date_to_f': '2020-05-06',
            'line_ids': lines
        })
        res = wizard_payment.generate_payments_action()
        domain = res.get('domain', False)

        payment = self.env['account.payment'].browse(domain[0][-1])
        lines = payment.move_line_ids.filtered('debit')

        ctx = {
            'payment_name': payment.name,
            'active_model': 'account.payment',
            'active_id': payment.id,
        }
        res = record.with_context(ctx).get_collect_data_parafiscal()

    def test_without_novelties_get_collect_data_parafiscal(self):
        record = self.FlatFile.new({
            'partner_id': self.account_payment.partner_id.id,
            'payment_description': "DEMO001",
            'file_type': 'get_collect_data_parafiscal',
            'template_modality': '1',
            'transaction_type': 'electronic_transaction',
            'template_type': 'E',
            'application_date': '2020-05-01',
        })

        self.settings_rules()

        self.payslip_without_novelties.compute_sheet()
        self.payslip_without_novelties.action_payslip_done()

        lines = self.env['account.move.line'].search([
            ('account_id.user_type_id', '=', self.payable_type_id.id)])
        wizard_payment = self.wizard_payment.new({
            'journal_id': self.journal_bank.id,
            'date_from_f': '2020-05-01',
            'date_to_f': '2020-05-06',
            'line_ids': lines
        })
        res = wizard_payment.generate_payments_action()
        domain = res.get('domain', False)

        payment = self.env['account.payment'].browse(domain[0][-1])
        lines = payment.move_line_ids.filtered('debit')

        ctx = {
            'payment_name': payment.name,
            'active_model': 'account.payment',
            'active_id': payment.id,
        }
        res = record.with_context(ctx).get_collect_data_parafiscal()

    def test_active_model_get_collect_data_parafiscal(self):
        record = self.FlatFile.new({
            'partner_id': self.account_payment.partner_id.id,
            'payment_description': "DEMO001",
            'file_type': 'get_collect_data_parafiscal',
            'template_modality': '1',
            'transaction_type': 'electronic_transaction',
            'template_type': 'E',
            'application_date': '2020-05-01',
        })
        res = record.get_collect_data_parafiscal()

        self.settings_rules()

        self.payslip.compute_sheet()
        self.payslip.action_payslip_done()
        lines = self.env['account.move.line'].search([
            ('account_id.user_type_id', '=', self.payable_type_id.id)])
        wizard_payment = self.wizard_payment.new({
            'journal_id': self.journal_bank.id,
            'date_from_f': '2020-05-01',
            'date_to_f': '2020-05-06',
            'line_ids': lines
        })
        res = wizard_payment.generate_payments_action()
        domain = res.get('domain', False)
        if domain and domain[0][-1]:
            payment = self.env['account.payment'].browse(domain[0][-1])
            lines = payment.move_line_ids.filtered('debit')
            ids = []
            for line in lines:
                res = line.full_reconcile_id\
                    .reconciled_line_ids.filtered('credit')
                if res.move_id.id:
                    ids.append(res.move_id.id)
            if len(ids) and ids[0]:
                self.payslip.write({
                    'move_id': ids[0]
                })

            self.env['ir.config_parameter'].sudo().set_param(
                'many2many.ibc_adjustment_rule_ids', [self.salary_rule_01.id])

            ctx = {
                'payment_name': payment.name,
                'active_model': 'account.payment',
                'active_id': payment.id,
            }
            res = record.with_context(ctx).get_collect_data_parafiscal()
            config = self.env['res.config.settings'].create({})
            config.vst_rule_ids = self.salary_rule.ids
            config.avp_rule_ids = self.salary_rule.ids
            config.sln_rule_ids = self.salary_rule.ids
            config.ige_rule_ids = self.salary_rule.ids
            config.lma_rule_ids = self.salary_rule.ids
            config.vac_lr_rule_ids = self.salary_rule.ids
            config.irl_rule_ids = self.salary_rule.ids
            config.integral_salary_structure_ids = [self.env.ref(
                'bits_hr_payroll_news.hr_payroll_structure_employee_02').id]
            config.execute()
            res = record.with_context(ctx).get_collect_data_parafiscal()
            self.settlement.write({'payslip_id': self.payslip.id})
            self.contract.write(
                {'date_start': datetime.now()+timedelta(days=-365)})
            self.payslip.line_ids.filtered(
                lambda line: line.code == '001').write(
                {'payroll_news_id': [(6, 0, [self.payroll_new.id])]})

            new = self.env['social.security'].search([
                ('entity_type', '=', 'risk_class'),
                ('code', '=', '1')], limit=1)
            # Transferencias
            self.env['social.security.transfer'].create({
                'employee_id': self.employee.id,
                'request_date': datetime.now(),
                'social_security_new': new.id,
                'entity_type': 'risk_class',
                'state': 'validate',
                'date_start': datetime.now(),
                'date_end': datetime.now()+timedelta(days=10),
            })

            new = self.env['social.security'].search([
                ('entity_type', '=', 'arl'),
                ('code', '=', '14-8')], limit=1)
            # Transferencias
            self.env['social.security.transfer'].create({
                'employee_id': self.employee.id,
                'request_date': datetime.now(),
                'social_security_new': new.id,
                'entity_type': 'risk_class',
                'state': 'validate',
                'date_start': datetime.now(),
                'date_end': datetime.now()+timedelta(days=10),
            })

            res = record.with_context(ctx).get_collect_data_parafiscal()

    def test_without_active_model_get_collect_data_parafiscal(self):
        record = self.FlatFile.new({
            'partner_id': self.account_payment.partner_id.id,
            'payment_description': "DEMO001",
            'file_type': 'get_collect_data_parafiscal',
            'template_modality': '1',
            'transaction_type': 'electronic_transaction',
            'template_type': 'E',
            'application_date': '2020-05-01',
        })
        ctx = {
            'payment_name': self.account_payment.name,
            'active_model': 'account.payment',
            'active_id': self.account_payment.id,
        }
        res = record.with_context(ctx).get_collect_data_parafiscal()

    def test_days_30_get_collect_data_parafiscal(self):
        record = self.FlatFile.new({
            'partner_id': self.account_payment.partner_id.id,
            'payment_description': "DEMO001",
            'file_type': 'get_collect_data_parafiscal',
            'template_modality': '1',
            'transaction_type': 'electronic_transaction',
            'template_type': 'E',
            'application_date': '2020-05-01',
        })
        res = record.get_collect_data_parafiscal()

        self.settings_rules()

        self.env['hr.contract.history'].search([
            ('_type', '=', 'wage'),
            ('contract_id', '=', self.payslip.contract_id.id)
        ]).unlink()

        self.novelty.employee_payroll_news_ids[0].write({
            'quantity': 31
        })

        self.novelty.write({
            'request_date_from': datetime.strptime(
                '2020-12-22', '%Y-%m-%d'
            ),
            'request_date_to': datetime.strptime(
                '2020-12-22', '%Y-%m-%d'
            )
        })

        self.payslip.compute_sheet()

        self.payslip.line_ids\
            .filtered(lambda x: x.code == '001')\
            .write({'code': '3010'})
        self.payslip.line_ids\
            .filtered(lambda x: x.code == '002')\
            .write({'code': '3020'})

        self.payslip.action_payslip_done()
        lines = self.env['account.move.line'].search([
            ('account_id.user_type_id', '=', self.payable_type_id.id)])
        wizard_payment = self.wizard_payment.new({
            'journal_id': self.journal_bank.id,
            'date_from_f': '2020-05-01',
            'date_to_f': '2020-05-06',
            'line_ids': lines
        })
        res = wizard_payment.generate_payments_action()
        domain = res.get('domain', False)
        if domain and domain[0][-1]:
            payment = self.env['account.payment'].browse(domain[0][-1])
            lines = payment.move_line_ids.filtered('debit')
            ids = []
            for line in lines:
                res = line.full_reconcile_id\
                    .reconciled_line_ids.filtered('credit')
                if res.move_id.id:
                    ids.append(res.move_id.id)
            if len(ids) and ids[0]:
                self.payslip.write({
                    'move_id': ids[0]
                })

            self.env['ir.config_parameter'].sudo().set_param(
                'many2many.ibc_adjustment_rule_ids', [self.salary_rule_01.id])

            self.env['ir.config_parameter'].sudo().set_param(
                'many2many.non_apply_box_rule_ids', [self.salary_rule_01.id])

            self.env['ir.config_parameter'].sudo().set_param(
                'many2many.integral_salary_structure_ids',
                [self.payroll_structure.id])

            self.env['ir.config_parameter'].sudo().set_param(
                'many2many.sena_salary_structure_ids',
                [self.payroll_structure.id])

            ctx = {
                'payment_name': payment.name,
                'active_model': 'account.payment',
                'active_id': payment.id,
            }
            res = record.with_context(ctx).get_collect_data_parafiscal()
            config = self.env['res.config.settings'].create({})
            config.vst_rule_ids = self.salary_rule.ids
            config.avp_rule_ids = self.salary_rule.ids
            config.sln_rule_ids = self.salary_rule.ids
            config.ige_rule_ids = self.salary_rule.ids
            config.lma_rule_ids = self.salary_rule.ids
            config.vac_lr_rule_ids = self.salary_rule.ids
            config.irl_rule_ids = self.salary_rule.ids
            config.integral_salary_structure_ids = [self.env.ref(
                'bits_hr_payroll_news.hr_payroll_structure_employee_02').id]
            config.execute()
            res = record.with_context(ctx).get_collect_data_parafiscal()
            self.settlement.write({'payslip_id': self.payslip.id})

            self.payslip.line_ids.filtered(
                lambda line: line.code == '001').write(
                {'payroll_news_id': self.payroll_new.id})

            new = self.env['social.security'].search([
                ('entity_type', '=', 'risk_class'),
                ('code', '=', '1')], limit=1)
            # Transferencias
            self.env['social.security.transfer'].create({
                'employee_id': self.employee.id,
                'request_date': datetime.now(),
                'social_security_new': new.id,
                'entity_type': 'risk_class',
                'state': 'validate',
                'date_start': datetime.now(),
                'date_end': datetime.now()+timedelta(days=10),
            })

            new = self.env['social.security'].search([
                ('entity_type', '=', 'arl'),
                ('code', '=', '14-8')], limit=1)
            # Transferencias
            self.env['social.security.transfer'].create({
                'employee_id': self.employee.id,
                'request_date': datetime.now(),
                'social_security_new': new.id,
                'entity_type': 'risk_class',
                'state': 'validate',
                'date_start': datetime.now(),
                'date_end': datetime.now()+timedelta(days=10),
            })

            res = record.with_context(ctx).get_collect_data_parafiscal()

    def test_get_config_rules(self):
        record = self.FlatFile.new({
            'partner_id': self.account_payment.partner_id.id,
            'payment_description': "DEMO001",
            'file_type': 'get_collect_data_parafiscal',
            'template_modality': '1',
            'transaction_type': 'electronic_transaction',
            'template_type': 'E',
            'application_date': '2020-05-01',
        })
        ctx = {
            'payment_name': self.account_payment.name,
            'active_model': 'account.payment',
            'active_id': self.account_payment.id,
        }
        row = {'end': 1, 'start': 0, 'type': 'N', 'long': '4'}
        localdict = dict(VSP=True, VSP_DATE=datetime.now())
        res = record.with_context(ctx).get_contract_variation(self.payslip)
        res = record.with_context(ctx).compute_field_42(
            row, self.payslip, 1, localdict, 100)
        res = record.with_context(ctx).compute_field_43(
            row, self.payslip, 1, localdict, 100)
        res = record.with_context(ctx).compute_field_44(
            row, self.payslip, 1, localdict, 100)
        res = record.with_context(ctx).compute_field_45(
            row, self.payslip, 1, localdict, 100)
        res = record.with_context(ctx).compute_field_95(
            row, self.payslip, 1, localdict, 100)
        res = record.with_context(ctx).compute_field_82(
            row, self.payslip, 1, localdict)
        res = record.with_context(ctx).compute_field_46(
            row, self.payslip, 1, localdict, [])
        res = record.with_context(ctx).compute_field_54(
            row, self.payslip, 1, localdict, [])
        res = record.with_context(ctx).get_config_rules(self.payslip)

    def settings_rules(self):
        self.env['ir.config_parameter'].sudo().set_param(
            'many2many.vst_rule_ids', [self.salary_rule.id])

        self.env['ir.config_parameter'].sudo().set_param(
            'many2many.sln_rule_ids',
            [self.salary_rule.id, self.salary_rule_01.id])

        self.env['ir.config_parameter'].sudo().set_param(
            'many2many.ige_rule_ids',
            [self.salary_rule.id, self.salary_rule_01.id])

        self.env['ir.config_parameter'].sudo().set_param(
            'many2many.lma_rule_ids',
            [self.salary_rule.id, self.salary_rule_01.id])

        self.env['ir.config_parameter'].sudo().set_param(
            'many2many.vac_lr_rule_ids',
            [self.salary_rule.id, self.salary_rule_01.id])

        self.env['ir.config_parameter'].sudo().set_param(
            'many2many.avp_rule_ids', [self.salary_rule.id])

        self.env['ir.config_parameter'].sudo().set_param(
            'many2many.irl_rule_ids',
            [self.salary_rule.id, self.salary_rule_01.id])

    def test_date(self):
        record = self.FlatFile.new({
            'partner_id': self.account_payment.partner_id.id,
            'payment_description': "DEMO001",
            'file_type': 'get_collect_data_parafiscal',
            'template_modality': '1',
            'transaction_type': 'electronic_transaction',
            'template_type': 'E',
            'application_date': '2020-05-01',
        })
        record.last_day_of_month(date(2021, 1, 25))

    def test_diferente_csv_execute(self):
        record = self.FlatFile.new({
            'partner_id': self.account_payment.partner_id.id,
            'payment_description': "DEMO001",
            'file_type': 'get_collect_data_parafiscal',
            'template_modality': '1',
            'transaction_type': 'electronic_transaction',
            'template_type': 'E',
            'application_date': '2020-05-01',
            'file_extension': 'csv'
        })

        self.payslip_without_novelties.compute_sheet()
        self.payslip_without_novelties.action_payslip_done()

        lines = self.env['account.move.line'].search([
            ('account_id.user_type_id', '=', self.payable_type_id.id)])
        wizard_payment = self.wizard_payment.new({
            'journal_id': self.journal_bank.id,
            'date_from_f': '2020-05-01',
            'date_to_f': '2020-05-06',
            'line_ids': lines
        })
        res = wizard_payment.generate_payments_action()
        domain = res.get('domain', False)

        payment = self.env['account.payment'].browse(domain[0][-1])
        lines = payment.move_line_ids.filtered('debit')

        ctx = {
            'payment_name': payment.name,
            'active_model': 'account.payment',
            'active_id': payment.id,
        }
        res = record.with_context(ctx).get_collect_data_parafiscal()
