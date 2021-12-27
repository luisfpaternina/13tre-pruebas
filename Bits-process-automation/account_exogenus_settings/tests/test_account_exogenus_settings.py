from odoo.tests.common import TransactionCase
from datetime import datetime, timedelta, date
from odoo.exceptions import ValidationError
from odoo.tests.common import Form
from odoo.addons.account_exogenus_settings.controllers.main import (Main)
import unittest
import logging
from io import BytesIO


class TestAccountExogenusSettings(TransactionCase):
    def setUp(self):
        super(TestAccountExogenusSettings, self).setUp()
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
        self.account_move = self.env[
            'account.move']
        self.account_journal = self.env[
            'account.journal']

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

        self.column_configuration_1 = self.AccountColumnConfiguration.create({
            'name': "Numero de identificación",
            # 'condition_select': "python",
            'condition_python': "partner_id.vat"
        })

        self.column_configuration_2 = self.AccountColumnConfiguration.create({
            'name': "codigo",
            # 'condition_select': "python",
            'condition_python': "partner_id.vat"
        })

        self.format_1 = self.AccountFormatExogenus.create({
            'name': "Formato 1001 test",
            'code': "1001111",
            'format_type': "dian",
        })

        self.format_2 = self.AccountFormatExogenus.create({
            'name': "Formato 1002 test",
            'code': "2222222",
            'format_type': "dian",
        })

        self.format_colum_1 = self.AccountExogenusFormatColumn.create({
            'account_format_id': self.format_1.id,
            'account_column_id': self.column_configuration_1.id,
            'sequence': 1,
        })

        self.format_colum_2 = self.AccountExogenusFormatColumn.create({
            'account_format_id': self.format_1.id,
            'account_column_id': self.column_configuration_2.id,
            'sequence': 1
        })

        self.format_2 = self.AccountFormatExogenus.create({
            'name': "Formato 2 testeo",
            'code': "002299",
            'format_type': "dian",
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

        self.AccountConceptExogenusLine_1 = self.\
            AccountConceptExogenusLine.create({
                'name': "001",
                'account_code': "1111"
            })

        self.AccountAccountType_1 = self.AccountAccountType.create({
            'name': "account type",
            'type': "other",
            'internal_group': 'equity'
            })

        self.AccountAccount_1 = self.AccountAccount.create({
            'name': 'Test Account 1',
            'code': '51236873',
            'user_type_id': self.AccountAccountType_1.id,
            'company_id': self.env.company.id
        })

        self.AccountAccount_2 = self.AccountAccount.create({
            'name': 'Test Account 2',
            'code': '51236883',
            'user_type_id': self.AccountAccountType_1.id,
            'company_id': self.env.company.id
        })

        self.wizard_exogenus_1 = self.WizardAccountExogenusPrintXls.create({
            'date_from': date(2020, 1, 1),
            'date_to': date(2020, 2, 1),
            'format_id': self.format_1.id
        })

    def test_check_exist_record_in_lines_with_raise(self):
        with self.assertRaises(ValidationError):
            self.format_1.write({
                    'account_column_ids': [(0, 0, {
                        'account_format_id': self.format_1.id,
                        'account_column_id': self.column_configuration_1.id,
                        'sequence': 1,
                        })]
            })
            self.format_1._check_exist_record_in_lines()

    def test_check_exist_record_in_lines(self):
        self.format_1._check_exist_record_in_lines()

    """
    def test_check_dates(self):
        self.wizard_account_exogenus_1._check_dates()
    """
    def test_check_dates_with_raise(self):
        with self.assertRaises(ValidationError):
            self.wizard_exogenus_1.write({
                                'date_from': date(2020, 2, 1),
                                'date_to': date(2020, 1, 1),
                                })

    def test_init_buffer(self):
        output = BytesIO()
        output = self.wizard_exogenus_1._init_buffer(output)
        output.seek(0)
        self.wizard_exogenus_1._init_buffer(output)

    def test_action_generate_xlsx_report(self):
        self.wizard_exogenus_1.action_generate_xlsx_report()

    def test_file_name(self):
        self.wizard_exogenus_1.file_name()

    def test_document_print(self):
        self.wizard_exogenus_1.document_print()

    def test_generate_xlsx(self):
        self.wizard_exogenus_1.format_id.account_column_ids.create({
            'account_format_id': self.format_2.id,
            'account_column_id': self.column_configuration_2.id,
            'sequence': 10,
            })
        output = BytesIO()
        output = self.wizard_exogenus_1._init_buffer(output)
        output.seek(0)

        self.wizard_exogenus_1.generate_xlsx(output)
