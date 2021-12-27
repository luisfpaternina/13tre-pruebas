# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class HrContract(models.Model):
    _inherit = 'hr.contract'

    salary_aid_ids = fields.One2many(
        'hr.contract.salary.aid',
        'contract_id',
        string='salary aid'
    )

    type_contract = fields.Selection([
        ('1', 'Fixed term contract'),
        ('2', 'Indefinite term contract'),
        ('3', 'Work or labor'),
        ('4', 'Learning'),
        ('5', 'Internships')],
        default="1"
    )

    contributor_type_id = fields.Many2one(
        'social.security',
        _('Contributor Type'),
        domain="[('entity_type', '=', 'contributor_type')]",
        required=True
    )

    def searchSalaryAid(self, aid_code):
        # self represent the employee contract
        salaryAid = next(
            (aid for aid in self.salary_aid_ids
             if aid.salary_aid_id.code == aid_code),
            None)

        # if exist the salary aid into employee contrat, calcule the value
        if salaryAid:
            return salaryAid.value/30
        else:
            return 0

    @api.model_create_multi
    def create(self, vals):
        for val in vals:
            self._validate_field_required(val)

        return super(HrContract, self).create(vals)

    @api.model
    def _validate_field_required(self, val):
        if not val.get('structure_type_id'):
            raise ValidationError(
                _("The field 'structure_type_id' is required")
            )
