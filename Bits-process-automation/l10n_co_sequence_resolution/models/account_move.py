# -*- coding: utf-8 -*-

from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class AccountInvoice(models.Model):
    _inherit = 'account.move'

    def _get_warn_resolution(self):
        self.ensure_one()
        warn_remaining = False
        warn_inactive_resolution = False

        if self.journal_id.sequence_id.use_dian_control:
            remaining_numbers = self.journal_id.sequence_id.remaining_numbers
            remaining_days = self.journal_id.sequence_id.remaining_days
            date_range = self.env['ir.sequence.date_range'].search([
                ('sequence_id', '=', self.journal_id.sequence_id.id),
                ('active_resolution', '=', True)])
            today = fields.Datetime.today().date()
            if date_range:
                date_range.ensure_one()
                date_to = date_range.date_to
                days = (date_to - today).days
                numbers = date_range.number_to - date_range.number_next_actual
                warn_remaining = True \
                    if numbers < remaining_numbers or days < remaining_days \
                    else False
            else:
                warn_inactive_resolution = True

        self.warn_inactive_resolution = warn_inactive_resolution
        self.warn_remaining = warn_remaining

    warn_remaining = fields.Boolean(
        string="Warn About Remainings?",
        compute="_get_warn_resolution",
        store=False)
    warn_inactive_resolution = fields.Boolean(
        string="Warn About Inactive Resolution?",
        compute="_get_warn_resolution",
        store=False)

    def _get_text_info(self):
        self.ensure_one()
        sequence_id = self.journal_id.sequence_id
        self.active_resolution = sequence_id.date_range_ids.filtered('active_resolution')
        if self.active_resolution:
            msg = _('Official document of the authorization of '
                    'electronic invoicing <br/>No %s validity %s months'
                    ' %s to %s <br/>that enables from %s to %s.<br/>' % (
                    self.name, "07", self.active_resolution.date_from, self.active_resolution.date_to,
                    self.active_resolution.number_from, self.active_resolution.number_to))
            return msg
        return ""
