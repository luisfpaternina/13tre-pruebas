from datetime import datetime, date, timedelta
from odoo.addons.account_difference_instead.tests.common \
    import TestAccountDifference


class TestAccountDifferenceInstead(TestAccountDifference):

    def setUp(self):
        super(TestAccountDifferenceInstead, self).setUp()

    # Test execute cron without assigned accounts and journal
    def test_execute_cron(self):
        self.account_move._cron_execute_unrealized_exchange_difference()
        self.account_payment.post()

    # Test execute cron with assigned accounts and journal
    def test_config_settings(self):

        # Assign accounts and journal
        self.env['ir.config_parameter'].sudo().set_param(
            'account_difference_instead.unrealized_exchange_vendors',
            self.account_1.id)
        self.env['ir.config_parameter'].sudo().set_param(
            'account_difference_instead.unrealized_exchange_customers',
            self.account_1.id)
        self.env['ir.config_parameter'].sudo().set_param(
            'account_difference_instead.unrealized_exchange_expenses',
            self.account_2.id)
        self.env['ir.config_parameter'].sudo().set_param(
            'account_difference_instead.unrealized_exchange_income',
            self.account_3.id)
        self.env['ir.config_parameter'].sudo().set_param(
            'account_difference_instead.unrealized_exchange_journal',
            self.account_journal.id)

        # Execute Cron
        self.account_move._cron_execute_unrealized_exchange_difference()

    # Test execute cron with assigned accounts and journal
    # and test second process
    def test_less_rate_exchange(self):

        # Assign accounts and journal
        self.env['ir.config_parameter'].sudo().set_param(
            'account_difference_instead.unrealized_exchange_vendors',
            self.account_1.id)
        self.env['ir.config_parameter'].sudo().set_param(
            'account_difference_instead.unrealized_exchange_customers',
            self.account_1.id)
        self.env['ir.config_parameter'].sudo().set_param(
            'account_difference_instead.unrealized_exchange_expenses',
            self.account_2.id)
        self.env['ir.config_parameter'].sudo().set_param(
            'account_difference_instead.unrealized_exchange_income',
            self.account_3.id)
        self.env['ir.config_parameter'].sudo().set_param(
            'account_difference_instead.unrealized_exchange_journal',
            self.account_journal.id)

        # Execute Cron
        self.account_move._cron_execute_unrealized_exchange_difference()

        # Add new rate to other currency
        self.other_currency.write({
            "active": True,
            "rate_ids": [(0, 0, {
                'name': date(2020, 3, 1),
                'rate': 1.1
            })]
        })
        # Execute Cron
        self.account_move._cron_execute_unrealized_exchange_difference()

    def test_positive_payment(self):

        # Assign accounts and journal
        self.env['ir.config_parameter'].sudo().set_param(
            'account_difference_instead.unrealized_exchange_vendors',
            self.account_1.id)
        self.env['ir.config_parameter'].sudo().set_param(
            'account_difference_instead.unrealized_exchange_customers',
            self.account_1.id)
        self.env['ir.config_parameter'].sudo().set_param(
            'account_difference_instead.unrealized_exchange_expenses',
            self.account_2.id)
        self.env['ir.config_parameter'].sudo().set_param(
            'account_difference_instead.unrealized_exchange_income',
            self.account_3.id)
        self.env['ir.config_parameter'].sudo().set_param(
            'account_difference_instead.unrealized_exchange_journal',
            self.account_journal.id)

        # Execute Cron
        self.account_move._cron_execute_unrealized_exchange_difference()

        self.account_payment.post()

    def test_negative_payment(self):

        # Assign accounts and journal
        self.env['ir.config_parameter'].sudo().set_param(
            'account_difference_instead.unrealized_exchange_vendors',
            self.account_1.id)
        self.env['ir.config_parameter'].sudo().set_param(
            'account_difference_instead.unrealized_exchange_customers',
            self.account_1.id)
        self.env['ir.config_parameter'].sudo().set_param(
            'account_difference_instead.unrealized_exchange_expenses',
            self.account_2.id)
        self.env['ir.config_parameter'].sudo().set_param(
            'account_difference_instead.unrealized_exchange_income',
            self.account_3.id)
        self.env['ir.config_parameter'].sudo().set_param(
            'account_difference_instead.unrealized_exchange_journal',
            self.account_journal.id)

        # Execute Cron
        self.account_move._cron_execute_unrealized_exchange_difference()

        # Add new rate to other currency
        self.other_currency.write({
            "active": True,
            "rate_ids": [(0, 0, {
                'name': date(2020, 3, 1),
                'rate': 0.1
            })]
        })
        # Execute Cron
        self.account_move._cron_execute_unrealized_exchange_difference()

        self.account_payment.post()

    def test_customer_invoice(self):
        # Assign accounts and journal
        self.env['ir.config_parameter'].sudo().set_param(
            'account_difference_instead.unrealized_exchange_vendors',
            self.account_1.id)
        self.env['ir.config_parameter'].sudo().set_param(
            'account_difference_instead.unrealized_exchange_customers',
            self.account_1.id)
        self.env['ir.config_parameter'].sudo().set_param(
            'account_difference_instead.unrealized_exchange_expenses',
            self.account_2.id)
        self.env['ir.config_parameter'].sudo().set_param(
            'account_difference_instead.unrealized_exchange_income',
            self.account_3.id)
        self.env['ir.config_parameter'].sudo().set_param(
            'account_difference_instead.unrealized_exchange_journal',
            self.account_journal.id)

        # Execute Cron
        self.account_move._cron_execute_unrealized_exchange_difference()

        # Add new rate to other currency
        self.other_currency.write({
            "active": True,
            "rate_ids": [(0, 0, {
                'name': date(2020, 3, 1),
                'rate': 0.1
            })]
        })
        # Execute Cron
        self.account_move._cron_execute_unrealized_exchange_difference()

        # Add new rate to other currency
        self.other_currency.write({
            "active": True,
            "rate_ids": [(0, 0, {
                'name': date(2020, 4, 1),
                'rate': 0.2
            })]
        })
        # Execute Cron
        self.account_move._cron_execute_unrealized_exchange_difference()

        self.account_payment2.post()
