from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api


class SocialSecurityTranfer(models.Model):
    _name = 'social.security.transfer'
    _description = 'bits_social_security_history.bits_social_security_history'

    employee_id = fields.Many2one(
        'hr.employee',
        required=True,
        string="Employee",
        help='Select corresponding Employee'
    )

    entity_type = fields.Selection([
        ('health', 'Eps'),
        ('pension', 'Pension'),
        ('arl', 'Arl'),
        ('compensation_box', 'Compensation Box'),
        ('contributor_type', 'Contributor Type'),
        ('contributor_subtype', 'Contributor Subtype'),
        ('layoffs', 'Layoffs'),
        ('risk_class', 'Risk Class')],
        string="Type",
        required=True
    )

    request_date = fields.Date(
        string='Request Date',
        required=True
    )

    social_security_new = fields.Many2one(
        'social.security',
        domain="[('entity_type', '=', entity_type)]",
        required=True
    )

    social_security_old = fields.Many2one(
        'social.security',
        domain="[('entity_type', '=', entity_type)]",
    )

    state = fields.Selection(
        [('draft', 'Draft'),
            # State for validation process
         ('validate', 'Validate'),
            # State for completion of the validation process
         ('done', 'Done'),
         ('cancel', 'Cancel')],
        'Status', copy=False, default='draft')

    date_start = fields.Date(
        string='Initial date',
        default=datetime.now().strftime('%Y-%m-01'))
    date_end = fields.Date(
        string='End date',
        default=str(datetime.now() + relativedelta(
            months=+1, day=1, days=-1))[:10])

    validation_date = fields.Date(
        string="Validation Date"
    )

    @api.onchange('entity_type', 'employee_id')
    def _onchange_entity_type(self):
        self.ensure_one()
        if self.employee_id and self.entity_type:
            dict_entity = {
                'health': (
                    self.employee_id.health
                    if self.employee_id.health else False
                ),
                'pension': (
                    self.employee_id.pension
                    if self.employee_id.pension else False
                ),
                'arl': (
                    self.employee_id.arl
                    if self.employee_id.arl else False
                ),
                'compensation_box': (
                    self.employee_id.compensation_box
                    if self.employee_id.compensation_box else False
                ),
                'contributor_type': (
                    self.employee_id.contributor_type
                    if self.employee_id.contributor_type else False
                ),
                'contributor_subtype': (
                    self.employee_id.contributor_subtype
                    if self.employee_id.contributor_subtype else False
                ),
                'risk_class': (
                    self.employee_id.contract_id.risk_class
                    if self.employee_id.contract_id.risk_class else False
                ),
                'layoffs': (
                    self.employee_id.layoffs
                    if self.employee_id.layoffs else False
                )
            }
            self.social_security_old = dict_entity.get(f"{self.entity_type}", 0)

        if self.employee_id and self.entity_type:
            if self.social_security_new != "":
                self.write({'social_security_new': ''})

    def action_validate(self):
        self.write({'state': 'validate'}),
        self.write({'validation_date': datetime.now()})

    def action_done(self):
        self.write({'state': 'done'})
        if self.employee_id and self.social_security_new:
            if self.entity_type == 'health':
                self.employee_id.health = self.social_security_new
            elif self.entity_type == 'pension':
                self.employee_id.pension = self.social_security_new
            elif self.entity_type == 'arl':
                self.employee_id.arl = self.social_security_new
            elif self.entity_type == 'compensation_box':
                self.employee_id.compensation_box = self.social_security_new
            elif self.entity_type == 'contributor_type':
                self.employee_id.contributor_type = self.social_security_new
            elif self.entity_type == 'contributor_subtype':
                self.employee_id.contributor_subtype = self.social_security_new
            elif self.entity_type == 'risk_class':
                (
                    self.employee_id
                        .contract_id
                        .risk_class
                ) = self.social_security_new
            else:
                self.employee_id.layoffs = self.social_security_new

    def action_set_to_cancel(self):
        self.write({'state': 'cancel'})

    def action_set_to_draft(self):
        self.write({'state': 'draft'})
