from odoo import models, fields, api, _


class HrSalaryRuleAccount(models.Model):
    _name = 'hr.salary.rule.account'
    _description = ('represents intermediate table'
                    ', an salary rule can have many account account')

    salary_rule_id = fields.Many2one('hr.salary.rule', string=_('Salary rule'))
    salary_rule_code = fields.Char(string=_('Salary Rule Code'))
    struct_id = fields.Many2one(
        'hr.payroll.structure', string=_('Salary Structure'),
        related="salary_rule_id.struct_id")
    account_account_id = fields.Many2one(
        'account.account', string=_('Accounting accounts'), required=True)
    account_code = fields.Char(string=_('Account Code'))
    account_analytic_id = fields.Many2one(
        'account.analytic.account', string=_('Center cost'))
    analytic_code = fields.Char(string=_('Analytic Code'))
    account_type = fields.Selection([
        ('credit', "Credit"),  # Acreedora
        ('debit', "Debit")  # Deudora
    ], string=_('Account type'), required=True)
    social_security_id = fields.Many2one(
        'social.security', string=_('Social Security')
    )
    social_security_code = fields.Char(string=_('Social Security Code'))
    _sql_constraints = [
        ('uk_hr_salary_rule_account',
         'unique(salary_rule_id,'
         'account_account_id, account_analytic_id, account_type)',
         'You cannot have the same accounting accounts'
         'assigned more than once')
    ]

    @api.model
    def create(self, vals):
        self.code_homologation(vals)
        result = super(HrSalaryRuleAccount, self).create(vals)
        return result

    def code_homologation(self, vals):
        code = ''
        if 'account_code' in vals:
            code = vals.get('account_code', False)
            vals['account_account_id'] = self.code_search(
                'account.account', code, 'code')
        if 'analytic_code' in vals:
            code = vals.get('analytic_code', False)
            vals['account_analytic_id'] = self.code_search(
                'account.analytic.account', code, 'code')
        if 'social_security_code' in vals:
            code = vals.get('social_security_code', False)
            vals['social_security_id'] = self.code_search(
                'social.security', code, 'code')
        if 'salary_rule_code' in vals:
            code = vals.get('salary_rule_code', False)
            vals['salary_rule_id'] = self.code_search(
                'hr.salary.rule', code, 'import_code')

    def code_search(self, model, code, field):
        result = (self.env[model].search(
            [(field, '=', code)]) if code else False)
        return result.id if result else False
