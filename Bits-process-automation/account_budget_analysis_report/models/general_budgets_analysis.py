from odoo import fields, models, tools, api


class GeneralBudgetAnalysis(models.Model):
    _name = 'general.budget.analysis'
    _description = 'this is a general budget report'
    _auto = False
    _order = 'date_from DESC'

    crossovered_budget_state = fields.Selection(
        string='State',
        selection=[
            ('draft', 'Draft'),
            ('cancel', 'Cancelled'),
            ('confirm', 'Confirmed'),
            ('validate', 'Validated'),
            ('done', 'Done')
            ],
        readonly=True)
    general_budget_id = fields.Many2one(
        'account.budget.post',
        string='Budgetary Position',
        readonly=True)
    analytic_account_id = fields.Many2one(
        'account.analytic.account',
        string='Analytic Account',
        readonly=True)
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        readonly=True)
    date_from = fields.Date(string='Start Date', readonly=True)
    date_to = fields.Date(string='End Date', readonly=True)
    paid_date = fields.Date(string='Paid Date', readonly=True)
    planned_amount = fields.Float(string='Planned Amount', readonly=True)
    practical_amount = fields.Float(
        string='Practical Amount',
        compute="_compute_amount")
    theoritical_amount = fields.Float(
        string='Theoretical Amount',
        compute="_compute_amount")

    @api.depends('general_budget_id',
                 'analytic_account_id',
                 'company_id',
                 'date_from',
                 'date_to')
    def _compute_amount(self):
        for rec in self:
            practical_amount = 0
            theoritical_amount = 0
            budget_obj = self\
                .env['crossovered.budget.lines']\
                .search([
                        ('general_budget_id', '=', rec.general_budget_id.id),
                        ('analytic_account_id', '=',
                            rec.analytic_account_id.id),
                        ('company_id', '=', rec.company_id.id),
                        ('date_from', '=', rec.date_from),
                        ('date_to', '=', rec.date_to),
                        ])
            for budget in budget_obj:
                practical_amount += budget.practical_amount
                theoritical_amount += budget.theoritical_amount
            rec.practical_amount = practical_amount
            rec.theoritical_amount = theoritical_amount

    def init(self):
        tools.drop_view_if_exists(self._cr, self._table)
        query = """
            CREATE VIEW %s AS (
                SELECT
                ROW_NUMBER() OVER (ORDER BY cbl.general_budget_id) AS id,
                cb.state as crossovered_budget_state,
                cbl.general_budget_id,
                cbl.analytic_account_id,
                cbl.company_id,
                cbl.date_from,
                cbl.date_to,
                cbl.paid_date,
                sum(cbl.planned_amount) as planned_amount
                FROM
                crossovered_budget_lines cbl
                LEFT JOIN crossovered_budget cb
                ON (cbl.crossovered_budget_id = cb.id)
                GROUP BY cb.state,
                cbl.general_budget_id,
                cbl.analytic_account_id,
                cbl.company_id,
                cbl.date_from,
                cbl.date_to,
                cbl.paid_date
               )
        """ % self._table
        self._cr.execute(query)
