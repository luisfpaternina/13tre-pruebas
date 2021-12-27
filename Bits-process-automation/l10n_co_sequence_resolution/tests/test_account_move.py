# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError
from odoo.addons.l10n_co_sequence_resolution.tests.common \
    import TestSequenceResolutionBase
from odoo.tests.common import Form
from odoo.tests import tagged


class TestAccountMove(TestSequenceResolutionBase):

    def setUp(self):
        super(TestAccountMove, self).setUp()

    def test_create_account_move_resolution_dian(self):
        invoice = self.env['account.move'].create(self.invoice_dicc)

        invoice._get_warn_resolution()

        invoice.journal_id.write({'sequence_id': self.ir_sequence.id})

        invoice._get_warn_resolution()

        date_range = self.env['ir.sequence.date_range'].search([
            ('sequence_id', '=', self.ir_sequence.id),
            ('active_resolution', '=', True)])
        date_range.write({'active_resolution': False})
        with self.assertRaises(ValidationError):
            invoice.journal_id.sequence_id._next()

        invoice._get_warn_resolution()
        self.ir_sequence.write({
            'remaining_numbers': 0,
        })
        date_range.write({
            'active_resolution': True,
            'number_next_actual': 100,
        })
        invoice._get_warn_resolution()
