# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import logging
_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    transportation_allowance = fields.Float(
        string=_("Transportation allowance"),
        related='company_id.transportation_allowance',
        readonly=False
    )

    @api.onchange('transportation_allowance')
    def _compute_transportation_allowance(self):
        self._check_there_is_transportation()
        second_check = self._search_rule_object()
        if second_check is False:
            return
        else:
            for rule in second_check:
                rule.amount_fix = self.transportation_allowance / 30

    def _search_rule_object(self):
        answer = self.env['hr.salary.rule'].\
            search([('l10n_type_rule', '=', 'connectivity_rule')])
        answer = list(answer)
        if len(answer) > 0:
            return answer
        return False

    def _check_there_is_transportation(self):
        if self.transportation_allowance:
            if self.transportation_allowance > 0 \
                    or self.transportation_allowance == 0.0:
                return True
            else:
                raise ValidationError(_(
                    'Esta tratando de ingresar una \
                        cantidad negativa.'
                ))
        else:
            return False


class ResCompany(models.Model):
    _inherit = 'res.company'
    transportation_allowance = fields.Float(
        string=_("transportation_allowance")
    )
