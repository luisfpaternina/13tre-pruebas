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
        self.AccountMove = self.env[
            'account.move']
        self.AccountMoveLine = self.env[
            'account.move.line']
        self.ResPartner = self.env[
            'res.partner']
        self.ResCompany = self.env[
            'res.company']
        self.AccountAccount = self.env[
            'account.account']
        self.AccountAccountType = self.env[
            'account.account.type']
        self.AccountJournal = self.env[
            'account.journal']
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

        self.ResCompany_1 = self.ResCompany.create({
            'name': "TST Company",
            'extract_show_ocr_option_selection': 'manual_send'
        })

        self.ResPartner_1 = self.ResPartner.create({
            'name': "Bits Americas"
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

        self.AccountJournal_1 = self.AccountJournal.create({
            'name': 'Test Journal',
            'type': 'general',
            'code': 'TSTJ1',
            'company_id': self.env.company.id
        })

        self.column_configuration_1 = self.AccountColumnConfiguration.create({
            'name': "Numero de identificación",
            'condition_python': "partner_id.vat"
        })

        self.column_configuration_2 = self.AccountColumnConfiguration.create({
            'name': "codigo",
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
            'code': "11111",
            'name': "account test",
            'create_asset': 'draft',
            'user_type_id': self.AccountAccountType_1.id

        })

        self.wizard_exogenus_1 = self.WizardAccountExogenusPrintXls.create({
            'date_from': date(2020, 1, 1),
            'date_to': date(2020, 2, 1),
            'format_id': self.format_1.id
        })

        self.AccountColumnConfiguration_1 = self.\
            AccountColumnConfiguration.create({
                'name': 'Test Account column',
                'code': 'CODTEST',
                })

    def test_execute_code(self):
        move_line = self.env['account.move.line']
        wiz = self.env['wizard.account.exogenus.print.xls']
        self.AccountColumnConfiguration_1.execute_code(move_line, wiz)
