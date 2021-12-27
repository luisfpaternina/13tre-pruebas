from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestAccountAssetReportNiifGolgap(TransactionCase):

    def setUp(self):
        super(TestAccountAssetReportNiifGolgap, self).setUp()
        self.previous_options = {
            'unfolded_lines': [],
            'date': {
                'string': '2021',
                'period_type': 'fiscalyear',
                'mode': 'range',
                'strict_range': False,
                'date_from': '2021-01-01',
                'date_to': '2021-12-31',
                'filter': 'this_year'
            },
            'all_entries': False,
            'hierarchy': False,
            'niif_colgap_asset': [
                {
                    'id': 'niif',
                    'name': 'NIIF',
                    'selected': False
                },
                {
                    'id': 'fiscal',
                    'name': 'Fiscal',
                    'selected': True
                }
            ],
            'unfold_all': True,
            'unposted_in_period': True,
            'self': 'account.assets.report()'
        }
        self.options = {
            'unfolded_lines': [],
            'date':
            {
                'string': '2021',
                'period_type': 'fiscalyear',
                'mode': 'range',
                'strict_range': False,
                'date_from': '2021-01-01',
                'date_to': '2021-12-31',
                'filter': 'this_year'
            },
            'all_entries': False,
            'hierarchy': False
        }
        self.asset_report = self.env['account.assets.report']

    def test_init_filter_asset_niif_colgap(self):
        self.asset_report._init_filter_niif_colgap_asset(
            self.options, self.previous_options)

    def test_filter_niif_colgap_asset_none(self):
        self.asset_report.filter_niif_colgap_asset = None
        self.asset_report._init_filter_niif_colgap_asset(
            self.options, self.previous_options)

    def test_test_init_filter_assetNiifColgap_without_niif_colgap_asset(self):
        self.previous_options.pop('niif_colgap_asset')
        self.asset_report._init_filter_niif_colgap_asset(
            self.options, self.previous_options)

    def test_get_assets_lines_without_niif_colgap_asset(self):
        self.asset_report._get_assets_lines(self.options)

    def test_get_assets_lines(self):
        self.options['niif_colgap_asset'] = [
            {
                'id': 'niif',
                'name': 'NIIF',
                'selected': False
            },
            {
                'id': 'fiscal',
                'name': 'Fiscal',
                'selected': True
            }
        ]
        self.asset_report._get_assets_lines(self.options)

    def test_get_assets_lines_without_all_entries(self):
        self.options['all_entries'] = True
        self.asset_report._get_assets_lines(self.options)
