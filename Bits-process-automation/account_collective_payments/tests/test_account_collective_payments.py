from datetime import date
from odoo.addons.account_collective_payments.tests.common \
    import TestAccountCollectivePaymentsBase
from odoo.exceptions import UserError, ValidationError


class TestAccountCollectivePayments(TestAccountCollectivePaymentsBase):

    def setUp(self):
        super(TestAccountCollectivePayments, self).setUp()

    def test_onchange_line_list_invalid(self):
        record = self.wizard_ref.new({
            'date_from_f': '2020-05-06',
            'date_to_f': '2020-05-01'
        })
        res = record._onchange_line_list()
        self.assertTrue(res.get('warning', False))

    def test_onchange_line_list_valid(self):
        record = self.wizard_ref.new({
            'date_from_f': '2020-05-01',
            'date_to_f': '2020-05-06'
        })
        res = record._onchange_line_list()

        # Basic domain
        self.assertTrue(res.get('domain', False))
        lines = res.get('domain', False)
        self.assertTrue(lines.get('line_ids', False))
        domain = lines.get('line_ids', False)

        self.assertEqual(len(domain), 5)

        # Compose domain
        record.journal_id_f = self.journal_id
        record.account_id_f = self.account_id
        record.partner_id_f = self.partner_id
        record.journal_type_f = self.journal_id.type
        res = record._onchange_line_list()
        self.assertTrue(res.get('domain', False))
        lines = res.get('domain', False)
        self.assertTrue(lines.get('line_ids', False))
        domain = lines.get('line_ids', False)

        self.assertEqual(len(domain), 8)

    def test_clean_lines_action(self):
        lines = self.env['account.move.line'].search([])

        record = self.wizard_ref.new({
            'date_from_f': '2020-05-01',
            'date_to_f': '2020-05-06',
            'line_ids': lines
        })
        record._onchange_line_ids()
        record.clean_lines = True
        record._onchange_line_ids()
        self.assertEqual(len(record.line_ids), 0)

    def test_filter_bank(self):
        record = self.wizard_ref.create({
            'date_from_f': '2020-05-01',
            'date_to_f': '2020-05-06',
            'journal_id': self.journal_bank.id,
            'bank_id': self.bank_id[0].id
        })
        record._onchange_line_list()

    def test_generate_payments_action(self):
        lines = self.env['account.move.line'].search([
            ('account_id.user_type_id', '=', self.payable_type_id.id)])

        record = self.wizard_ref.new({
            'journal_id': self.journal_bank.id,
            'date_from_f': '2020-05-01',
            'date_to_f': '2020-05-06',
            'line_ids': lines
        })
        record.generate_payments_action()
        self.wizard_ref.generate_payments_action()

    def test_generate_journal_entry(self):
        lines = self.env['account.move.line'].search([
            ('account_id.user_type_id', '=', self.payable_type_id.id)])
        line_id = lines[0]
        values = {
            'journal_id': self.journal_bank.id,
            'payment_method_id': self.payment_method.id,
            'payment_date': date(2020, 5, 7),
            'communication': " ",
            'payment_type': 'outbound',
            'amount': abs(line_id.amount_residual),
            'currency_id': self.company_id.currency_id.id,
            'partner_id': self.company_id.partner_id.id,
            'partner_type': "supplier",
            'state': "draft"
        }
        sequence_code = 'account.payment.supplier.invoice'
        values['name'] = self.env['ir.sequence'].next_by_code(
            sequence_code, sequence_date=date(2020, 5, 7))
        payment_id = self.account_payment.create(values)

        record = self.wizard_ref.new({
            'date_from_f': '2020-05-01',
            'date_to_f': '2020-05-06',
            'line_ids': [(6, 0, [line_id.id])]
        })
        record._generate_journal_entry(payment_id)

    def test_generate_journal_entry_not_sequence_payment(self):
        lines = self.env['account.move.line'].search([
            ('account_id.user_type_id', '=', self.payable_type_id.id)])
        line_id = lines[0]
        values = {
            'journal_id': self.journal_bank.id,
            'payment_method_id': self.payment_method.id,
            'payment_date': date(2020, 5, 7),
            'communication': " ",
            'payment_type': 'outbound',
            'amount': abs(line_id.amount_residual),
            'currency_id': self.company_id.currency_id.id,
            'partner_id': self.company_id.partner_id.id,
            'partner_type': "supplier",
            'state': "draft"
        }
        sequence_code = 'account.payment.supplier.invoice'
        sequence = self.env['ir.sequence'].search(
            [('code', '=', sequence_code)])
        sequence.unlink()
        payment_id = self.account_payment.create(values)

        record = self.wizard_ref.new({
            'date_from_f': '2020-05-01',
            'date_to_f': '2020-05-06',
            'line_ids': [(6, 0, [line_id.id])]
        })
        with self.assertRaises(UserError):
            record._generate_journal_entry(payment_id)

    def test_get_different_currency_payment(self):
        lines = self.env['account.move.line'].search([
            ('account_id.user_type_id', '=', self.payable_type_id.id)])
        line_id = lines[0]
        values = {
            'journal_id': self.journal_bank.id,
            'payment_method_id': self.payment_method.id,
            'payment_date': date(2020, 5, 7),
            'communication': " ",
            'payment_type': 'outbound',
            'amount': abs(line_id.amount_residual),
            'currency_id': self.other_currency.id,
            'partner_id': self.company_id.partner_id.id,
            'partner_type': "supplier",
            'state': "draft"
        }
        payment_id = self.account_payment.create(values)

        record = self.wizard_ref.new({
            'date_from_f': '2020-05-01',
            'date_to_f': '2020-05-06',
            'line_ids': [(6, 0, [line_id.id])]
        })
        write_off_amount = (
            payment_id.payment_difference_handling == 'reconcile'
            and -payment_id.payment_difference or 0.0)
        record._get_currency_payment(
            payment_id, payment_id.amount, write_off_amount)

    def test_get_some_currency_payment(self):
        lines = self.env['account.move.line'].search([
            ('account_id.user_type_id', '=', self.payable_type_id.id)])
        line_id = lines[0]
        self.journal_bank.currency_id = self.other_currency_1.id
        values = {
            'journal_id': self.journal_bank.id,
            'payment_method_id': self.payment_method.id,
            'payment_date': date(2020, 5, 7),
            'communication': " ",
            'payment_type': 'outbound',
            'amount': abs(line_id.amount_residual),
            'currency_id': self.other_currency.id,
            'partner_id': self.company_id.partner_id.id,
            'partner_type': "supplier",
            'state': "draft"
        }
        payment_id = self.account_payment.create(values)

        record = self.wizard_ref.new({
            'date_from_f': '2020-05-01',
            'date_to_f': '2020-05-06',
            'line_ids': [(6, 0, [line_id.id])]
        })
        company_currency = self.company_id.currency_id
        record._get_liquidity_account_currency(payment_id, company_currency,
                                               payment_id.amount,
                                               self.company_id.currency_id,
                                               payment_id.amount)

    def test_get_some_currency_payment_not_equal(self):
        lines = self.env['account.move.line'].search([
            ('account_id.user_type_id', '=', self.payable_type_id.id)])
        line_id = lines[0]
        self.journal_bank.currency_id = self.other_currency_1.id
        values = {
            'journal_id': self.journal_bank.id,
            'payment_method_id': self.payment_method.id,
            'payment_date': date(2020, 5, 7),
            'communication': " ",
            'payment_type': 'outbound',
            'amount': abs(line_id.amount_residual),
            'currency_id': self.other_currency.id,
            'partner_id': self.company_id.partner_id.id,
            'partner_type': "supplier",
            'state': "draft"
        }
        payment_id = self.account_payment.create(values)

        record = self.wizard_ref.new({
            'date_from_f': '2020-05-01',
            'date_to_f': '2020-05-06',
            'line_ids': [(6, 0, [line_id.id])]
        })
        company_currency = self.other_currency
        record._get_liquidity_account_currency(payment_id, company_currency,
                                               payment_id.amount,
                                               self.company_id.currency_id,
                                               payment_id.amount)

    def test_get_some_currency_payment_equal(self):
        lines = self.env['account.move.line'].search([
            ('account_id.user_type_id', '=', self.payable_type_id.id)])
        line_id = lines[0]
        self.journal_bank.currency_id = self.other_currency_1.id
        values = {
            'journal_id': self.journal_bank.id,
            'payment_method_id': self.payment_method.id,
            'payment_date': date(2020, 5, 7),
            'communication': " ",
            'payment_type': 'outbound',
            'amount': abs(line_id.amount_residual),
            'currency_id': self.other_currency.id,
            'partner_id': self.company_id.partner_id.id,
            'partner_type': "supplier",
            'state': "draft"
        }
        payment_id = self.account_payment.create(values)

        record = self.wizard_ref.new({
            'date_from_f': '2020-05-01',
            'date_to_f': '2020-05-06',
            'line_ids': [(6, 0, [line_id.id])]
        })
        company_currency = self.other_currency_1
        record._get_liquidity_account_currency(payment_id, company_currency,
                                               payment_id.amount,
                                               self.company_id.currency_id,
                                               payment_id.amount)

    def test_generate_payments_action_reconciled(self):
        lines = self.env['account.move.line'].search([
            ('account_id.user_type_id', '=', self.payable_type_id.id)])
        record = self.wizard_ref.new({
            'journal_id': self.journal_bank.id,
            'date_from_f': '2020-05-01',
            'date_to_f': '2020-05-06',
            'line_ids': lines
        })
        res = record.generate_payments_action()
        domain = res.get('domain', False)

        if domain and domain[0][-1]:
            payment = self.env['account.payment'].browse(domain[0][-1])
            self.assertEqual(payment.state, 'posted')

    def test_onchange_journal_process_type(self):
        record = self.wizard_ref.new({
            'date_from_f': '2020-05-01',
            'date_to_f': '2020-05-06',
        })
        res = record._onchange_process_type()
        self.assertTrue(res.get('domain', False))
        domain = res.get('domain', False)
        journal_id = domain.get('journal_id_f', False)
        res = record._onchange_journal_id_f()
        domain = res.get('domain', False)
        account_id = domain.get('account_id_f', False)
        record.journal_type_f = self.journal_id.type
        record.journal_id_f = self.journal_bank.id

        account_ids = self.account_account.search([])
        self.journal_bank.write({
            'account_control_ids': account_ids.ids
        })
        res = record._onchange_process_type()
        self.assertTrue(res.get('domain', False))
        domain = res.get('domain', False)
        self.assertTrue(domain.get('journal_id_f', False))
        res = record._onchange_journal_id_f()
        domain = res.get('domain', False)
        account_id = domain.get('account_id_f', False)

    def test_generate_payments_action_group_apply(self):
        lines = self.env['account.move.line'].search([
            ('account_id.user_type_id', '=', self.payable_type_id.id)])
        record = self.wizard_ref.create({
            'journal_id': self.journal_bank.id,
            'date_from_f': '2020-05-01',
            'date_to_f': '2020-05-06',
            'group_apply': True,
            'line_ids': lines
        })
        res = record.generate_payments_action()
        domain = res.get('domain', False)

        if domain and domain[0][-1]:
            payment = self.env['account.payment'].browse(domain[0][-1])
            self.assertEqual(payment.state, 'posted')

    def test_account_f(self):
        record = self.wizard_ref.new({
            'date_from_f': '2020-05-01',
            'date_to_f': '2020-05-06',
            'account_id_f': self.account_1.id
        })
        res = record._onchange_line_list()

    def test_get_devided_general_liquidity_line(self):
        lines = self.env['account.move.line'].search([
            ('account_id.user_type_id', '=', self.payable_type_id.id)])
        record = self.wizard_ref.create({
            'journal_id': self.journal_bank.id,
            'date_from_f': '2020-05-01',
            'date_to_f': '2020-05-06',
            'create_line_bank': True,
            'line_ids': lines
        })
        record.generate_payments_action()

    def test_get_devided_group_liquidity_line(self):
        lines = self.env['account.move.line'].search([
            ('account_id.user_type_id', '=', self.payable_type_id.id)])
        record = self.wizard_ref.create({
            'journal_id': self.journal_bank.id,
            'date_from_f': '2020-05-01',
            'date_to_f': '2020-05-06',
            'create_line_bank': True,
            'group_apply': True,
            'line_ids': lines
        })
        record.generate_payments_action()
