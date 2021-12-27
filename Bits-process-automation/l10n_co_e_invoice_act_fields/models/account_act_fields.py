# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.safe_eval import safe_eval


class AccountActFields(models.Model):
    _name = 'account.act.fields'
    _description = 'l10n_co_e_invoice_act_fields'

    name = fields.Char()
    code = fields.Char()
    description = fields.Text()

    mandatory = fields.Selection([
        ('optional', 'Optional'),
        ('required', 'Required'),
        ('condition', 'Conditional')],
        default='optional',
        required=True
    )

    condition_python = fields.Text(
        string='Python Condition',
        default='''
            # Available variables:
            #----------------------
            # account: object containing the account_move
            # Note: returned value have to be set in the variable 'result'

            result = account.name''',
        help='Code that is executed to bring the information.')

    condition_select = fields.Selection([
        ('none', 'Always True'),
        ('python', 'Python Expression')
    ], string="Condition Based on", default='none', required=True)

    validate_condition_select = fields.Text(
        string='Validate Condition',
        default='''
            # Available variables:
            #----------------------
            # account: object containing the account_move
            # Note: returned value have to be set in the variable 'result'

            result = account.name''',
        help='Applied this rule for calculation if condition is true.')

    _type = fields.Selection([('account', 'Account')], default='account')

    def _compute_rule(self, localdict):
        self.ensure_one()
        if not self.condition_python or self.condition_python == '':
            return False
        try:
            safe_eval(
                self.condition_python,
                localdict,
                mode='exec', nocopy=True)
            return localdict['result']
        except Exception as e:
            raise UserError(
                _('Wrong python code defined for active '
                  'field %s (%s).\nError: %s') % (self.name, self.code, e))

    def _satisfy_condition(self, localdict):
        self.ensure_one()
        if not self.condition_select or self.condition_select == 'none':
            return True
        try:
            safe_eval(
                self.validate_condition_select,
                localdict, mode='exec', nocopy=True)
            return localdict.get('result', False)
        except Exception as e:
            raise UserError(
                _('Wrong python condition defined for active '
                  'field %s (%s).\nError: %s') % (self.name, self.code, e))

    def validate_required_field(self, localdict):
        if not self._get_validate_required_field(localdict):
            raise UserError(
                _('Please enter data for the required field '
                  '%s.\nDescription: %s') % (self.name, self.description))
        return True

    def is_mandatory(self):
        return self.mandatory == 'required'

    def is_condition(self):
        return self.mandatory == 'condition'

    def _get_validate_required_field(self, localdict):
        try:
            safe_eval(
                self.condition_python,
                localdict,
                mode='exec', nocopy=True)
            result = localdict.get('result', False)
            if self.is_mandatory() and (result == '' or result is False):
                return False
            return True
        except Exception as e:
            if self.is_condition():
                return True
            return False
