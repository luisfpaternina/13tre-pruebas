from datetime import datetime, date, timedelta
from odoo.addons.account_bank_statement_conciliation.tests.common \
    import TestAccountStatement


class TestAccountStatementConciliation(TestAccountStatement):

    def setUp(self):
        super(TestAccountStatementConciliation, self).setUp()

    def test_domain_move_lines_for_reconciliation(self):
        self.reconciliation_widget.get_move_lines_for_bank_statement_line(
            self.account_bank_statement_1.line_ids.ids)

    def test_domain_move_lines_for_reconciliation_for_value(self):
        self.env['ir.config_parameter'].sudo().set_param(
            "account_statement_conciliation.conciliation_type",
            "value"
        )
        self.reconciliation_widget.get_move_lines_for_bank_statement_line(
            self.account_bank_statement_1.line_ids.ids)
