from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class DepreciationAssetCollective(models.TransientModel):
    _name = 'depreciation.asset.collective'

    depreciation_date = fields.Date('Depreciation Date')
    assets_depreciate = fields.Selection(
        string='Asset Depreciation',
        selection=[('all', 'All'), ('asset', 'Asset'),
                   ('intangible', 'Intangible')], default='all')

    # This method performs the massive depreciation of asset and intangible
    def depreciation_asset(self):
        domain = [('state', '=', 'open'),
                  ('asset_group', '=',  self.assets_depreciate)]
        if self.assets_depreciate == 'all':
            domain = [('state', '=', 'open'),
                      ('asset_group', 'in', ('asset', 'intangible'))]
        asset_ids = self.env['account.asset'].search(domain)
        if asset_ids:
            depreciation_lines_ids = self.env['account.move'].search(
                [('asset_id', 'in', tuple(asset_ids.ids)),
                 ('state', '=', 'draft'),
                 ('date', '<=', self.depreciation_date)])
            depreciation_lines_ids.post()
