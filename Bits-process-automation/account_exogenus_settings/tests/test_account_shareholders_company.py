from odoo.tests.common import TransactionCase
from datetime import datetime, timedelta, date
from odoo.exceptions import ValidationError
from odoo.tests.common import Form
from odoo.addons.account_exogenus_settings.controllers.main import (Main)
import unittest
import logging
from io import BytesIO


class TestAccountShareholdersCompany(TransactionCase):
    def setUp(self):
        super(TestAccountShareholdersCompany, self).setUp()
        self.Shareholders = self.env['account.shareholders.company']
        self.ResPartner = self.env['res.partner']

        self.res_partner_1 = self.ResPartner.create({
            "name": "Partner Test"
        })
        self.res_partner_2 = self.ResPartner.create({
            "name": "Partner Test 2"
        })
        self.shareholders_company_1 = self.Shareholders.create({
            "name": "Year 2021",
            "year": "2021",
            "liquid_assets": 1000,
            "total_number_shares": 200,
            "smaller_amounts": 50,
            "account_shareholders_company_line_ids": [(0, 0, {
                "partner_id": self.res_partner_1.id,
                "number_shares": 100,
                "percentage_share": 50
            }), (0, 0, {
                "partner_id": self.res_partner_2.id,
                "number_shares": 100,
                "percentage_share": 50
            })]
        })

    def tests_validate_number_of_shares(self):
        self.shareholders_company_1.write({
            "total_number_shares": 201
        })
        self.shareholders_company_1.onchange_number_shares()

    def tests_validate_number_of_shares_error(self):
        with self.assertRaises(ValidationError):
            self.shareholders_company_1.\
                account_shareholders_company_line_ids[0].\
                write({
                    "partner_id": self.res_partner_1.id,
                    "percentage_share": 50,
                    "number_shares": 1000,
                })
            self.shareholders_company_1.\
                account_shareholders_company_line_ids[1].\
                write({
                    "partner_id": self.res_partner_2.id,
                    "percentage_share": 50,
                    "number_shares": 100,
                })
            self.shareholders_company_1.write({
                "total_number_shares": 201
            })
            self.shareholders_company_1.onchange_number_shares()

    def tests_create_error_number_of_shares(self):
        with self.assertRaises(ValidationError):
            self.shareholders_company_1 = self.Shareholders.create({
                "name": "Year 2021",
                "year": "2021",
                "liquid_assets": 1000,
                "total_number_shares": 200,
                "smaller_amounts": 50,
                "account_shareholders_company_line_ids": [(0, 0, {
                    "partner_id": self.res_partner_1.id,
                    "number_shares": 0,
                    "percentage_share": 50
                }), (0, 0, {
                    "partner_id": self.res_partner_2.id,
                    "number_shares": 100,
                    "percentage_share": 50
                })]
            })
            self.shareholders_company_1.onchange_number_shares()

    def tests_write_error_number_of_shares(self):
        with self.assertRaises(ValidationError):
            self.shareholders_company_1.\
                account_shareholders_company_line_ids[0].write({
                    "number_shares": 0,
                })
            self.shareholders_company_1.onchange_number_shares()

    def tests_calc_percentage(self):
        self.shareholders_company_1.account_shareholders_company_line_ids[0]\
            ._calc_shareholder_contribution()

    def tests_calc_percentage_error(self):
        with self.assertRaises(ValidationError):
            self.shareholders_company_1.write({
                "total_number_shares": False,
            })
            self.shareholders_company_1.onchange_number_shares()
            self.shareholders_company_1.\
                account_shareholders_company_line_ids[0]\
                ._calc_shareholder_contribution()
