# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import time
from odoo import models, fields, api
from odoo.tools.misc import formatLang, format_date, get_lang
from odoo.tools.translate import _
from odoo.tools import append_content_to_html, DEFAULT_SERVER_DATE_FORMAT, html2plaintext
from odoo.exceptions import UserError


class AccountFollowupReport(models.AbstractModel):
    _inherit = 'account.followup.report'

    def _get_columns_name(self, options):
        """
        Override
        Return the name of the columns of the follow-ups report
        """
        headers = [{},
                   {'name': _('Date'), 'class': 'date', 'style': 'text-align:center; white-space:nowrap;'},
                   {'name': _('Due Date'), 'class': 'date', 'style': 'text-align:center; white-space:nowrap;'},
                   {'name': _('Credit Type'), 'style': 'text-align:center; white-space:nowrap;'},
                   {'name': _('Credit Invoice Number'), 'style': 'text-align:center; white-space:nowrap;'},
                   {'name': _('Source Document'), 'style': 'text-align:center; white-space:nowrap;'},
                   {'name': _('Communication'), 'style': 'text-align:right; white-space:nowrap;'},
                   {'name': _('Expected Date'), 'class': 'date', 'style': 'white-space:nowrap;'},
                   {'name': _('Excluded'), 'class': 'date', 'style': 'white-space:nowrap;'},
                   {'name': _('Total Due'), 'class': 'number o_price_total', 'style': 'text-align:right; white-space:nowrap;'}
                  ]
        if self.env.context.get('print_mode'):
            headers = headers[:7] + headers[9:]  # Remove the 'Expected Date' and 'Excluded' columns
        return headers

    def _get_lines(self, options, line_id=None):
        """
        Override
        Compute and return the lines of the columns of the follow-ups report.
        """
        # Get date format for the lang
        partner = options.get('partner_id') and self.env['res.partner'].browse(options['partner_id']) or False
        if not partner:
            return []

        lang_code = partner.lang if self._context.get('print_mode') else self.env.user.lang or get_lang(self.env).code
        lines = []
        res = {}
        today = fields.Date.today()
        line_num = 0
        for l in partner.unreconciled_aml_ids.filtered(lambda l: l.company_id == self.env.company):
            if l.company_id == self.env.company:
                if self.env.context.get('print_mode') and l.blocked:
                    continue
                currency = l.currency_id or l.company_id.currency_id
                if currency not in res:
                    res[currency] = []
                res[currency].append(l)
        for currency, aml_recs in res.items():
            total = 0
            total_issued = 0
            for aml in aml_recs:
                amount = aml.amount_residual_currency if aml.currency_id else aml.amount_residual
                date_due = format_date(self.env, aml.date_maturity or aml.date, lang_code=lang_code)
                total += not aml.blocked and amount or 0
                is_overdue = today > aml.date_maturity if aml.date_maturity else today > aml.date
                is_payment = aml.payment_id
                if is_overdue or is_payment:
                    total_issued += not aml.blocked and amount or 0
                if is_overdue:
                    date_due = {'name': date_due, 'class': 'color-red date', 'style': 'white-space:nowrap;text-align:center;color: red;'}
                if is_payment:
                    date_due = ''
                move_line_name = self._format_aml_name(aml.name, aml.move_id.ref, aml.move_id.name)
                if self.env.context.get('print_mode'):
                    move_line_name = {'name': move_line_name, 'style': 'text-align:right; white-space:normal;'}
                amount = formatLang(self.env, amount, currency_obj=currency)
                line_num += 1
                expected_pay_date = format_date(self.env, aml.expected_pay_date, lang_code=lang_code) if aml.expected_pay_date else ''
                invoice_origin = aml.move_id.invoice_origin or ''
                if len(invoice_origin) > 43:
                    invoice_origin = invoice_origin[:40] + '...'
                
                # Get Credit Information
                if aml.move_id and aml.move_id.credit_line_id:
                    credit_line = aml.move_id.credit_line_id
                    credit_type = credit_line.credit_id.credit_type_id.name
                    invoice_number = credit_line.credit_id.invoice_number
                else:
                    credit_type = ''
                    invoice_number = ''

                columns = [
                    format_date(self.env, aml.date, lang_code=lang_code),
                    date_due,
                    credit_type,
                    invoice_number,
                    invoice_origin,
                    move_line_name,
                    (expected_pay_date and expected_pay_date + ' ') + (aml.internal_note or ''),
                    {'name': '', 'blocked': aml.blocked},
                    amount,
                ]
                if self.env.context.get('print_mode'):
                    columns = columns[:6] + columns[8:]
                lines.append({
                    'id': aml.id,
                    'account_move': aml.move_id,
                    'name': aml.move_id.name,
                    'caret_options': 'followup',
                    'move_id': aml.move_id.id,
                    'type': is_payment and 'payment' or 'unreconciled_aml',
                    'unfoldable': False,
                    'columns': [type(v) == dict and v or {'name': v} for v in columns],
                })
            total_due = formatLang(self.env, total, currency_obj=currency)
            line_num += 1
            lines.append({
                'id': line_num,
                'name': '',
                'class': 'total',
                'style': 'border-top-style: double',
                'unfoldable': False,
                'level': 3,
                'columns': [{'name': v} for v in [''] * (5 if self.env.context.get('print_mode') else 7) + [total >= 0 and _('Total Due') or '', total_due]],
            })
            if total_issued > 0:
                total_issued = formatLang(self.env, total_issued, currency_obj=currency)
                line_num += 1
                lines.append({
                    'id': line_num,
                    'name': '',
                    'class': 'total',
                    'unfoldable': False,
                    'level': 3,
                    'columns': [{'name': v} for v in [''] * (5 if self.env.context.get('print_mode') else 7) + [_('Total Overdue'), total_issued]],
                })
            # Add an empty line after the total to make a space between two currencies
            line_num += 1
            lines.append({
                'id': line_num,
                'name': '',
                'class': '',
                'style': 'border-bottom-style: none',
                'unfoldable': False,
                'level': 0,
                'columns': [{} for col in columns],
            })
        # Remove the last empty line
        if lines:
            lines.pop()
        return lines

    @api.model
    def _build_followup_summary_with_field(self, field, options):
        """
        Build the followup summary based on the relevent followup line.
        :param field: followup line field used as the summary "template"
        :param options: dict that should contain the followup level and the partner
        :return: the summary if a followup line exists or None
        """
        followup_line = self.get_followup_line(options)
        if followup_line:
            partner = self.env['res.partner'].browse(options['partner_id'])
            lang = partner.lang or get_lang(self.env).code
            summary = followup_line.with_context(lang=lang)[field]
            try:
                document_type = dict(
                    partner._fields['l10n_co_document_type'].selection
                ).get(
                    partner.l10n_co_document_type
                )

                summary = summary % {'partner_name': partner.name,
                                     'partner_identification': partner.number_identification or partner.vat or '',
                                     'partner_identification_type': document_type or '',
                                     'date': format_date(self.env, fields.Date.today(), lang_code=partner.lang),
                                     'user_signature': html2plaintext(self.env.user.signature or ''),
                                     'company_name': self.env.company.name,
                                     'amount_due': formatLang(self.env, partner.total_due, currency_obj=partner.currency_id), 
                                     }
            except ValueError as exception:
                message = _("An error has occurred while formatting your followup letter/email. (Lang: %s, Followup Level: #%s) \n\nFull error description: %s") \
                          % (lang, followup_line.id, exception)
                raise ValueError(message)
            return summary
        raise UserError(_('You need a least one follow-up level in order to process your follow-up'))


class FollowupLine(models.Model):
    _inherit = 'account_followup.followup.line'
    
    @api.constrains('description')
    def _check_description(self):
        for line in self:
            if line.description:
                try:
                    line.description % {'partner_name': '', 'partner_identification': '', 'partner_identification_type': '', 'date': '', 'user_signature': '', 'company_name': '', 'amount_due': ''}
                except (TypeError, ValueError, KeyError):
                    raise Warning(_('Your description is invalid, use the right legend or %% if you want to use the percent character.'))

    @api.constrains('sms_description')
    def _check_sms_description(self):
        for line in self:
            if line.sms_description:
                try:
                    line.sms_description % {'partner_name': '', 'partner_identification': '', 'partner_identification_type': '', 'date': '', 'user_signature': '', 'company_name': '', 'amount_due': ''}
                except (TypeError, ValueError, KeyError):
                    raise Warning(_('Your sms description is invalid, use the right legend or %% if you want to use the percent character.'))
