# -*- coding: utf-8 -*-

import pytz
from dateutil import tz
from datetime import datetime

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class IrSequence(models.Model):
    _inherit = 'ir.sequence'

    use_dian_control = fields.Boolean(
        'Use DIAN control resolutions',
        default=False)

    remaining_numbers = fields.Integer(
        string='Remaining Numbers')
    remaining_days = fields.Integer(
        string='Remaining Days')
    dian_type = fields.Selection(
        [('computer_generated_invoice', 'Computer Generated Invoice'),
         ('paper_invoice', 'Paper Invoice'),
         ('pos_invoice', 'POS Invoice')],
        default='computer_generated_invoice', string='DIAN Type')

    @api.model
    def create(self, vals):
        rec = super(IrSequence, self).create(vals)
        for sequence_id in rec:
            if sequence_id.use_dian_control:
                sequence_id.check_active_resolution()
            sequence_id.check_date_range_ids()
        return rec

    def write(self, vals):
        res = super(IrSequence, self).write(vals)
        for sequence_id in self:
            if sequence_id.use_dian_control:
                sequence_id.check_active_resolution()
            sequence_id.check_date_range_ids()
        return res

    @api.onchange('use_dian_control')
    def onchange_active_resolution(self):
        for sequence_id in self:
            sequence_id.use_date_range = True

    def check_active_resolution(self):
        sequence_id = self
        if sequence_id.use_dian_control:
            if sequence_id.implementation != 'no_gap':
                sequence_id.implementation = 'no_gap'
            if sequence_id.padding != 0:
                sequence_id.padding = 0
            if not sequence_id.use_date_range:
                sequence_id.use_date_range = True
            if sequence_id.suffix:
                sequence_id.suffix = False
            if sequence_id.number_increment != 1:
                sequence_id.number_increment = 1
            timezone = pytz.timezone(self.env.user.tz or 'America/Bogota')
            from_zone = tz.gettz('UTC')
            to_zone = tz.gettz(timezone.zone)
            date_now = datetime.now().replace(tzinfo=from_zone)
            date_now = date_now.astimezone(to_zone).strftime('%Y-%m-%d')
            current_date = fields.Datetime.from_string(date_now).date()
            for date_range_id in sequence_id.date_range_ids:
                number_next_actual = date_range_id.number_next_actual
                if (number_next_actual >= date_range_id.number_from
                        and number_next_actual <= date_range_id.number_to
                        and current_date >= date_range_id.date_from
                        and current_date <= date_range_id.date_to):
                    if not date_range_id.active_resolution:
                        date_range_id.active_resolution = True
                    if date_range_id.prefix != sequence_id.prefix:
                        date_range_id.prefix = sequence_id.prefix
                else:
                    date_range_id.active_resolution = False
                if not date_range_id.prefix:
                    date_range_id.prefix = sequence_id.prefix
        return True

    def check_date_range_ids(self):
        msg1 = _('Final Date must be greater or equal than Initial Date.')
        msg2 = _('The Date Range must be unique or a date ' +
                 'must not be included in another Date Range.')
        msg3 = _('Number To must be greater or equal than Number From.')
        msg4 = _('The Number Next must be greater in one to Number To, ' +
                 'to represent a finished sequence or Number Next must be ' +
                 'included in Number Range.')
        msg5 = _('The system needs only one active DIAN resolution.')
        msg6 = _('The system needs at least one active DIAN resolution.')
        date_ranges = []
        _active_resolution = 0
        for date_range_id in self.date_range_ids:
            if date_range_id.date_from > date_range_id.date_to:
                raise ValidationError(msg1)
            date_ranges.append(
                (date_range_id.date_from, date_range_id.date_to)
            )
            date_ranges.sort(key=lambda date_range: date_range[0])
            date_from = False
            date_to = False
            i = 0
            for date_range in date_ranges:
                if i == 0:
                    date_from = date_range[0]
                    date_to = date_range[1]
                    i += 1
                    continue
                if date_to < date_range[0]:
                    date_from = date_range[0]
                    date_to = date_range[1]
                else:
                    raise ValidationError(msg2)
                i += 1
            number_next_actual = date_range_id.number_next_actual
            if date_range_id.number_from > date_range_id.number_to:
                raise ValidationError(msg3)
            if (number_next_actual > (date_range_id.number_to + 1)
               or date_range_id.number_from > number_next_actual):
                raise ValidationError(msg4)
            if date_range_id.active_resolution and self.use_dian_control:
                _active_resolution += 1
        if self.use_dian_control:
            if _active_resolution == 0:
                raise ValidationError(msg6)

    def _next(self, sequence_date=None):
        msg = _('There is no active authorized invoicing resolution.')
        date_ranges = self.date_range_ids.search(
            [('active_resolution', '=', True)])
        if self.use_dian_control and not date_ranges:
            raise ValidationError(msg)
        res = super(IrSequence, self)._next(sequence_date)
        if self.use_dian_control:
            self.check_active_resolution()
        return res
