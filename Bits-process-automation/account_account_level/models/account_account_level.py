# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.modules.module import get_module_resource


class AccountAccountLevel(models.Model):
    _inherit = 'account.account'

    level = fields.Selection([
        ("1", "Level 1"),
        ("2", "Level 2"),
        ("3", "Level 3"),
        ("4", "Level 4"),
        ("5", "Level 5"),
        ("6", "Level 6"),
        ("7", "Level 7")],
        string=_("Level")
    )
    depends_on = fields.Many2one(
        "account.account",
        string=_("Depends on")
    )

    @api.model
    def create(self, vals):
        if vals.get('level', False):
            self._set_validation(vals.get('level', False),
                                 vals.get('code', False))
        if vals.get('depends_on', False):
            depends_on = self.browse([vals.get('depends_on')])
            self._set_validation_dependency(
                vals.get('code', False), depends_on.code)
        account = super(AccountAccountLevel, self).create(vals)
        return account

    def write(self, vals):
        if vals.get('code', False) or vals.get('level', False):
            code = vals.get('code') if vals.get('code', False) else self.code
            level = (vals.get('level') if vals.get(
                'level', False) else self.level)
            self._set_validation(level, code)

        if vals.get('code', False) or vals.get('depends_on', False):
            code = vals.get('code') if vals.get('code', False) else self.code
            depends = vals.get('depends_on') if vals.get(
                'depends_on', False) else self.depends_on.id
            depends_on = self.browse([depends])
            self._set_validation_dependency(code, depends_on.code)

        return super(AccountAccountLevel, self).write(vals)

    @api.onchange('level')
    def _onchange_level(self):
        if self.code:
            self._set_validation(self.level, self.code)
        return False

    def _get_dict_level(self, code):
        levels = {
            '1': True if len(code) == 1 else False,
            '2': True if len(code) == 2 else False,
            '3': True if len(code) == 4 else False,
            '4': True if len(code) == 6 else False,
            '5': True if len(code) == 8 else False,
            '6': True if len(code) == 10 else False,
            '7': True if len(code) == 12 else False
        }
        return levels

    def _set_validation(self, level, code):
        level_validate = self._get_dict_level(code)
        if not level_validate.get(level):
            raise ValidationError(
                _('The number of digits entered for the '
                  'account does not correspond to the selected level'))

    @api.onchange('depends_on')
    def _onchange_depends_on(self):
        if self.code and self.depends_on.code:
            self._set_validation_dependency(self.code, self.depends_on.code)
        return False

    def _get_dict_code_depend(self, code, code_dependency):
        code = (
            True if code_dependency in code else False
        )
        return code

    def _set_validation_dependency(self, code, code_dependency):
        code_validate = self._get_dict_code_depend(code, code_dependency)
        if not code_validate:
            raise ValidationError(
                _('The field depends on does'
                  ' not correspond to the code entered'))
