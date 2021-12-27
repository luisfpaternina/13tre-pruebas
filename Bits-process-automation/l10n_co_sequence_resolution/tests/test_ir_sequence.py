# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError
from odoo.addons.l10n_co_sequence_resolution.tests.common \
    import TestSequenceResolutionBase
from odoo.tests.common import Form


class TestIrSequence(TestSequenceResolutionBase):

    def setUp(self):
        super(TestIrSequence, self).setUp()

    def test_create_resolution_sequence(self):
        ir_sequence2 = self.env['ir.sequence'].create({
            'name': 'SEQ',
            'padding': 4,
            'number_increment': 1,
        })
        ir_sequence2._next()
        self.ir_sequence._next()
        self.ir_sequence.date_range_ids.write({
            'active_resolution': False
        })
        ir_sequence2.write({
            'use_dian_control': False
        })

        self.ir_sequence.onchange_active_resolution()

    def test_check_active_resolution(self):
        resolution = self.env['ir.sequence.date_range'].search(
            [('sequence_id', '=', self.ir_sequence.id)])
        resolution.write({
            'number_next_actual': 101,
            'prefix': 'DEMO',
        })
        self.ir_sequence.check_active_resolution()
        resolution.write({
            'number_next_actual': 1,
        })
        self.ir_sequence.date_range_ids.write({
            'prefix': 'DEMO',
        })
        self.ir_sequence.write({
            'padding': 2,
            'number_increment': 200,
            'suffix': 'DEMO',
        })
        self.ir_sequence.check_active_resolution()
        self.ir_sequence.write({
            'use_dian_control': False
        })
        self.ir_sequence.check_active_resolution()

    def test_check_date_range_ids(self):
        resolution = self.env['ir.sequence.date_range'].search(
            [('sequence_id', '=', self.ir_sequence.id)])
        resolution.write({
            'date_to': datetime.now(),
            'date_from': datetime.now()+timedelta(days=365),
        })

        with self.assertRaises(ValidationError):
            self.ir_sequence.check_date_range_ids()

        sequences = self.env['ir.sequence'].search(
            [('use_dian_control', '=', True)])
        sequences.unlink()
        dian_resolution = {
            'sequence_id': False,
            'resolution_number': 1,
            'number_next_actual': 1,
            'date_from': '2020-01-01',
            'date_to': '2020-12-31',
            'number_from': 1,
            'number_to': 100,
            'active_resolution': True,
        }

        dian_resolution2 = dian_resolution.copy()
        dian_resolution2['date_from'] = "2020-11-01"
        dian_resolution2['date_to'] = "2021-12-31"
        dian_resolution2['active_resolution'] = False
        with self.assertRaises(ValidationError):
            ir_sequence = self.env['ir.sequence'].create({
                'name': 'TEST2',
                'use_dian_control': True,
                'dian_type': 'computer_generated_invoice',
                'date_range_ids': [
                    (0, 0, dian_resolution2),
                    (0, 0, dian_resolution),
                ]
            })

        dian_resolution2['date_from'] = "2021-01-01"
        dian_resolution2['date_to'] = "2021-12-31"
        ir_sequence = self.env['ir.sequence'].create({
            'name': 'TEST2',
            'use_dian_control': True,
            'dian_type': 'computer_generated_invoice',
            'date_range_ids': [
                (0, 0, dian_resolution2),
                (0, 0, dian_resolution),
            ]
        })
        dian_resolution2['number_from'] = 101
        dian_resolution2['number_to'] = 100

        with self.assertRaises(ValidationError):
            ir_sequence = self.env['ir.sequence'].create({
                'name': 'TEST2',
                'use_dian_control': True,
                'dian_type': 'computer_generated_invoice',
                'date_range_ids': [
                    (0, 0, dian_resolution2),
                    (0, 0, dian_resolution),
                ]
            })
        dian_resolution2['number_next_actual'] = 101
        dian_resolution2['number_from'] = 1
        dian_resolution2['number_to'] = 100

        with self.assertRaises(ValidationError):
            ir_sequence = self.env['ir.sequence'].create({
                'name': 'TEST2',
                'use_dian_control': True,
                'dian_type': 'computer_generated_invoice',
                'date_range_ids': [
                    (0, 0, dian_resolution2),
                ]
            })

        dian_resolution2['number_next_actual'] = 99
        dian_resolution2['number_from'] = 100
        dian_resolution2['number_to'] = 100
        with self.assertRaises(ValidationError):
            ir_sequence = self.env['ir.sequence'].create({
                'name': 'TEST2',
                'use_dian_control': True,
                'dian_type': 'computer_generated_invoice',
                'date_range_ids': [
                    (0, 0, dian_resolution2),
                ]
            })
        dian_resolution2 = dian_resolution.copy()
        dian_resolution2['date_from'] = datetime.now()-timedelta(days=365)
        dian_resolution2['date_to'] = datetime.now()-timedelta(days=1)
        with self.assertRaises(ValidationError):
            ir_sequence = self.env['ir.sequence'].create({
                'name': 'TEST2',
                'use_dian_control': True,
                'dian_type': 'computer_generated_invoice',
                'date_range_ids': [
                    (0, 0, dian_resolution2),
                ]
            })

    def test__onchange_number_from(self):
        resolution = self.env['ir.sequence.date_range'].search(
            [('sequence_id', '=', self.ir_sequence.id)], limit=1)
        resolution._onchange_number_from()
        resolution.number_from = 0
        resolution._onchange_number_from()
