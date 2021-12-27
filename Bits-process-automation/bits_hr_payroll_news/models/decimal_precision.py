import math

from odoo import api, fields, models, tools
from odoo.tools import float_round


class DecimalPrecision(models.Model):
    _inherit = 'decimal.precision'
    _description = 'Decimal Precision'

    rouding = fields.Float()
    multiple = fields.Float()

    @api.model
    @tools.ormcache('application')
    def get_rounding_rules(self, application):
        self.env.cr.execute(
            'select rouding, multiple from decimal_precision where name=%s',
            (application,)
        )
        res = self.env.cr.fetchone()
        rouding = res[0] if res[0] else -2
        multiple = res[1] if res[1] else 100.0
        return rouding, multiple

    @api.model
    @tools.ormcache('total', 'multiple')
    def roundup(self, total, multiple):
        return int(math.ceil(total / multiple)) * int(multiple)

    @api.model
    @tools.ormcache('application', 'total')
    def get_rounding(self, application, total):
        rouding, multiple = self.get_rounding_rules(application)
        factor = 1 if total > 0 else -1
        res = self.roundup(abs(total), multiple)
        return res * factor
