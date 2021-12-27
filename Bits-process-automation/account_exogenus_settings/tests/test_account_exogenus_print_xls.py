from odoo.tests.common import TransactionCase
from datetime import datetime, timedelta, date
from odoo.exceptions import ValidationError, UserError
from odoo.tests.common import Form
from odoo.addons.account_exogenus_settings.controllers.main import (Main)
import unittest
import logging
from io import BytesIO


class TestAccountExogenusSettings(TransactionCase):
    def setUp(self):
        super(TestAccountExogenusSettings, self).setUp()
        self.res_partner = self.env[
            'res.partner']
        self.res_company = self.env[
            'res.company']
        self.account_journal = self.env[
            'account.journal']
        self.account_move = self.env[
            'account.move']
        self.AccountMoveLine = self.env[
            'account.move.line']
        self.AccountConceptExogenus = self.env[
            'account.concept.exogenus']
        self.partners_shareholders_lines = self.env[
            'partners.shareholders.lines']
        self.AccountConceptExogenusLine = self.env[
            'account.concept.exogenus.line']
        self.PartnerShareholdersLiness = self.env[
            'partners.shareholders.lines']
        self.AccountAccount = self.env[
            'account.account']
        self.AccountAccountType = self.env[
            'account.account.type']
        self.AccountColumnConfiguration = self.env[
            'account.column.configuration']
        self.AccountColumnConfigurationLines = self.env[
            'account.column.configuration.lines']
        self.AccountExogenusFormatColumn = self.env[
            'account.exogenus.format.column']
        self.AccountFormatExogenus = self.env[
            'account.format.exogenus']
        self.WizardAccountExogenusPrintXls = self.env[
            'wizard.account.exogenus.print.xls']

        self.AccountAccountType_1 = self.AccountAccountType.create({
            'name': "account type",
            'type': "other",
            'internal_group': 'equity'
            })

        self.res_partner_1 = self.res_partner.create({
            'name': "TST Partner",
            'state_code': "11",
            'country_code': "169",
        })

        self.res_partner_2 = self.res_partner.create({
            'name': "Partner",
            'state_code': "043",
            'country_code': "313",
        })

        self.res_company_1 = self.res_company.create({
            'name': "TST Company",
            'extract_show_ocr_option_selection': 'manual_send'
        })

        self.AccountAccount_1 = self.AccountAccount.create({
            'name': 'Test Account 1',
            'code': '51236877',
            'user_type_id': self.env.ref(
                'account.data_account_type_current_assets').id,
            'company_id': self.env.company.id
        })
        self.AccountAccount_2 = self.AccountAccount.create({
            'name': 'Test Account 2',
            'code': '51236883',
            'user_type_id': self.env.ref(
                'account.data_account_type_current_assets').id,
            'company_id': self.env.company.id
        })

        self.journal = self.account_journal.create({
            'name': 'Test Journal',
            'type': 'general',
            'code': 'TSTJ1',
            'company_id': self.env.company.id
        })

        self.move_1 = self.account_move.create({
            'journal_id': self.journal.id,
            'date': date(2020, 5, 4),
            'type': 'entry',
            'company_id': self.env.company.id,
            'line_ids': [(0, 0, {
                'parent_state': 'posted',
                'account_id': self.AccountAccount_1.id,
                'partner_id': self.res_partner_1.id,
                'journal_id': self.journal.id,
                'company_id': self.env.company.id,
                'date': date(2020, 5, 4),
                'credit': 0.0,
                'debit': 1000.0
            }), (0, 0, {
                'parent_state': 'posted',
                'account_id': self.AccountAccount_2.id,
                'partner_id': self.res_partner_1.id,
                'journal_id': self.journal.id,
                'company_id': self.env.company.id,
                'date': date(2020, 5, 4),
                'credit': 1000.0,
                'debit': 0.0
            })]
        })

        self.move_2 = self.account_move.create({
            'journal_id': self.journal.id,
            'date': date(2020, 5, 4),
            'type': 'entry',
            'company_id': self.env.company.id,
            'line_ids': [(0, 0, {
                'parent_state': 'posted',
                'account_id': self.AccountAccount_1.id,
                'partner_id': self.res_partner_1.id,
                'journal_id': self.journal.id,
                'company_id': self.env.company.id,
                'date': date(2020, 5, 4),
                'credit': 0.0,
                'debit': 1000.0
            }), (0, 0, {
                'parent_state': 'posted',
                'account_id': self.AccountAccount_2.id,
                'partner_id': self.res_partner_1.id,
                'journal_id': self.journal.id,
                'company_id': self.env.company.id,
                'date': date(2020, 5, 4),
                'credit': 1000.0,
                'debit': 0.0
            })]
        })

        self.format_1 = self.AccountFormatExogenus.create({
            'name': "Formato 1001",
            'code': "1001111",
            'format_type': "dian",
            'bool_concept': True,
            'bool_lesser_amount': True
        })

        self.column_configuration_1 = self.AccountColumnConfiguration.create({
            'name': "Numero de identificación",
            'condition_python': "partner_id.vat",
            'bool_delete': False,
            'format_exogenus_id': self.format_1.id
        })

        self.column_configuration_2 = self.AccountColumnConfiguration.create({
            'name': "codigo",
            'condition_python': "partner_id.code",
            'bool_delete': False
        })

        self.format_2 = self.AccountFormatExogenus.create({
            'name': "Formato 1003 test",
            'code': "3222222",
            'format_type': "dian",
            'bool_concept': False,
            'bool_lesser_amount': False,
            'bool_amount': False
        })

        self.column_configuration_3 = self.AccountColumnConfiguration.create({
            'name': "Vat",
            'condition_python': "partner_id.vat",
            'bool_delete': False,
            'format_exogenus_id': self.format_2.id
        })

        self.format_3 = self.AccountFormatExogenus.create({
            'name': "Formato 1005",
            'code': "22222221",
            'format_type': "dian",
            'bool_concept': True,
            'bool_lesser_amount': False,
            'bool_amount': False
        })

        self.column_configuration_4 = self.AccountColumnConfiguration.create({
            'name': "Nombre",
            'condition_python': "partner_id.name",
            'bool_delete': False,
            'format_exogenus_id': self.format_3.id
        })

        self.format_4 = self.AccountFormatExogenus.create({
            'name': "Formato 1005",
            'code': "52222223",
            'format_type': "dian",
            'bool_concept': False,
            'bool_lesser_amount': True,
            'bool_amount': False
        })

        self.column_configuration_5 = self.AccountColumnConfiguration.create({
            'name': "Primer Nombre",
            'condition_python': "partner_id.vat",
            'bool_delete': False,
            'format_exogenus_id': self.format_4.id
        })

        self.format_5 = self.AccountFormatExogenus.create({
            'name': "Formato 1002 test",
            'code': "3252222",
            'format_type': "dian",
            'bool_concept': False,
            'bool_lesser_amount': False,
            'bool_amount': True
        })

        self.column_configuration_6 = self.AccountColumnConfiguration.create({
            'name': "Nombre",
            'condition_python': "partner_id.vat",
            'bool_delete': False,
            'format_exogenus_id': self.format_5.id
        })

        self.format_6 = self.AccountFormatExogenus.create({
            'name': "Formato 1002 test",
            'code': "3255222",
            'format_type': "dian",
            'bool_concept': False,
            'bool_lesser_amount': False,
            'partner_report': True
        })

        self.column_configuration_7 = self.AccountColumnConfiguration.create({
            'name': "Primer Apellido",
            'condition_python': "partner_id.vat",
            'bool_delete': False,
            'format_exogenus_id': self.format_6.id
        })

        self.format_colum_1 = self.AccountExogenusFormatColumn.create({
            'account_format_id': self.format_1.id,
            'account_column_id': self.column_configuration_1.id,
            'sequence': 0,
        })

        self.format_colum_2 = self.AccountExogenusFormatColumn.create({
            'account_format_id': self.format_1.id,
            'account_column_id': self.column_configuration_2.id,
            'sequence': 1
        })

        self.format_colum_3 = self.AccountExogenusFormatColumn.create({
            'account_format_id': self.format_2.id,
            'account_column_id': self.column_configuration_3.id,
            'sequence': 1
        })

        self.format_colum_4 = self.AccountExogenusFormatColumn.create({
            'account_format_id': self.format_3.id,
            'account_column_id': self.column_configuration_4.id,
            'sequence': 1
        })

        self.format_colum_5 = self.AccountExogenusFormatColumn.create({
            'account_format_id': self.format_4.id,
            'account_column_id': self.column_configuration_5.id,
            'sequence': 1
        })

        self.format_colum_6 = self.AccountExogenusFormatColumn.create({
            'account_format_id': self.format_5.id,
            'account_column_id': self.column_configuration_6.id,
            'sequence': 1
        })

        self.format_colum_7 = self.AccountExogenusFormatColumn.create({
            'account_format_id': self.format_6.id,
            'account_column_id': self.column_configuration_7.id,
            'sequence': 1
        })

        self.concept_1 = self.AccountConceptExogenus.create({
            'name': "Honorarios test",
            'code': "50021",
            'concept_code': True,
            'format_exogenus_id': self.format_1.id
        })

        self.concept_2 = self.AccountConceptExogenus.create({
            'name': "Comisiones test",
            'code': "500322",
            'concept_code': True,
            'format_exogenus_id': self.format_1.id
        })

        self.concept_3 = self.AccountConceptExogenus.create({
            'name': "Comisiones test",
            'code': "500322",
            'concept_code': True,
            'format_exogenus_id': self.format_2.id
        })

        self.AccountConceptExogenusLine_1 = self.\
            AccountConceptExogenusLine.create({
                'name': "001",
                'account_code': "1111",
                'account_id': self.AccountAccount_1.id,
                'concept_exogenus_id': self.concept_1.id
            })

        self.wizard_exogenus_1 = self.WizardAccountExogenusPrintXls.create({
            'date_from': date(2020, 1, 1),
            'date_to': date(2020, 10, 1),
            'format_id': self.format_1.id,
            'partner_id': self.res_partner_1.id
        })

        self.wizard_exogenus_2 = self.WizardAccountExogenusPrintXls.create({
            'date_from': date(2020, 1, 1),
            'date_to': date(2020, 10, 1),
            'format_id': self.format_3.id,
            'partner_id': self.res_partner_1.id
        })

        self.wizard_exogenus_3 = self.WizardAccountExogenusPrintXls.create({
            'date_from': date(2020, 1, 1),
            'date_to': date(2020, 10, 1),
            'format_id': self.format_2.id,
            'partner_id': self.res_partner_1.id,
            'company_id': self.res_company.id
        })

        self.wizard_exogenus_4 = self.WizardAccountExogenusPrintXls.create({
            'date_from': date(2020, 1, 1),
            'date_to': date(2020, 10, 1),
            'format_id': self.format_4.id,
            'partner_id': self.res_partner_2.id,
            'company_id': self.res_company.id
        })

        self.wizard_exogenus_5 = self.WizardAccountExogenusPrintXls.create({
            'date_from': date(2020, 1, 1),
            'date_to': date(2020, 10, 1),
            'format_id': self.format_5.id,
            'partner_id': self.res_partner_2.id,
            'company_id': self.res_company.id
        })

        self.wizard_exogenus_6 = self.WizardAccountExogenusPrintXls.create({
            'date_from': date(2020, 1, 1),
            'date_to': date(2020, 10, 1),
            'format_id': self.format_6.id,
            'partner_id': self.res_partner_2.id,
            'company_id': self.res_company.id
        })

    def test_check_exist_record_in_lines(self):
        with self.assertRaises(ValidationError):
            self.wizard_exogenus_1.write({
                'date_from': date(2020, 3, 1),
                'date_to': date(2020, 2, 1),
            })

    def test_init_buffer(self):
        self.move_1.post()
        output = '<_io.BytesIO object at 0x7fec763f1d60>'
        self.wizard_exogenus_1._init_buffer(output)

    def test_action_generate_xlsx_report(self):
        self.move_1.post()
        self.wizard_exogenus_1.action_generate_xlsx_report()

    def test_file_name(self):
        self.move_1.post()
        self.wizard_exogenus_1.file_name(file_format='xls')

    def test_get_domain(self):
        self.move_1.post()
        self.wizard_exogenus_3.write({
            'date_from': False,
            'date_to': False
        })
        self.wizard_exogenus_3._get_domain()

    def test_get_values(self):
        self.wizard_exogenus_3._get_domain()
        self.wizard_exogenus_3._get_values()

    def test_document_print(self):
        self.move_1.post()
        self.wizard_exogenus_1.document_print()

    def test_generate_xlsx(self):
        self.move_1.post()
        output = '<_io.BytesIO object at 0x7fb6dcf91090>'
        self.column_configuration_7.write({'bool_delete': True})
        self.wizard_exogenus_1.generate_xlsx(output)
        self.wizard_exogenus_2.generate_xlsx(output)
        self.wizard_exogenus_3.generate_xlsx(output)
        self.wizard_exogenus_4.generate_xlsx(output)
        self.wizard_exogenus_5.generate_xlsx(output)
        self.wizard_exogenus_6.generate_xlsx(output)

    def test_query_values_group_partner_concept_exogenus(self):
        self.move_1.post()
        self.wizard_exogenus_3._get_domain()
        self.wizard_exogenus_3._get_values()
        self.wizard_exogenus_3._query_values_group_partner_concept_exogenus()

    def test_query_values_group_partner_and_amount(self):
        self.move_1.post()
        self.wizard_exogenus_2._get_domain()
        self.wizard_exogenus_2._get_values()
        self.wizard_exogenus_2._query_values_group_partner_and_amount()

    def test_query_values_group_partner_and_account(self):
        self.move_1.post()
        self.wizard_exogenus_3._get_domain()
        self.wizard_exogenus_3._get_values()
        self.wizard_exogenus_3._query_values_group_partner_and_account()

    def test_query_values_group_concept_and_amount(self):
        self.move_1.post()
        self.wizard_exogenus_1._get_domain()
        self.wizard_exogenus_1._get_values()
        self.wizard_exogenus_1._query_values_group_concept_and_amount()
        self.format_1.write({
            'name': "test Format"
        })
        self.wizard_exogenus_1._get_domain()
        self.wizard_exogenus_1._get_values()
        self.wizard_exogenus_1._query_values_group_concept_and_amount()

    def test_query_values_art_4_6(self):
        self.move_1.post()
        self.wizard_exogenus_5._get_domain()
        self.wizard_exogenus_5._get_values()
        self.wizard_exogenus_5._query_values_art_4_6()

    def test_query_shareholders(self):
        self.move_1.post()
        self.wizard_exogenus_6._get_domain()
        self.wizard_exogenus_6._get_values()
        self.wizard_exogenus_6._query_shareholders()
