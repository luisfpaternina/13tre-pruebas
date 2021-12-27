from odoo import api, fields, models, _
from odoo.tools import format_date


class AssetsReport(models.AbstractModel):
    _inherit = 'account.assets.report'
    _description = 'Account Assets Report Niif Colgap'

    filter_niif_colgap_asset = True

    @api.model
    def _init_filter_niif_colgap_asset(self, options, previous_options=None):
        if self.filter_niif_colgap_asset is None:
            return

        if previous_options and previous_options.get('niif_colgap_asset'):
            asset_map = dict(
                (opt['id'], opt['selected'])
                for opt in previous_options.get('niif_colgap_asset')
                if 'selected' in opt
            )
        else:
            asset_map = {}
        options['niif_colgap_asset'] = [
            {'id': 'niif', 'name': 'NIIF', 'selected': asset_map.get('niif')},
            {'id': 'fiscal', 'name': 'Fiscal',
                'selected': asset_map.get('fiscal')},
        ]

    def _get_assets_lines(self, options):
        "Get the data from the database"

        self.env['account.move.line'].check_access_rights('read')
        self.env['account.asset'].check_access_rights('read')

        where_account_move = " AND state != 'cancel'"
        if not options.get('all_entries'):
            where_account_move = " AND state = 'posted'"

        sql = """
        -- remove all the moves that have
        -- been reversed from the search
        CREATE TEMPORARY TABLE IF NOT EXISTS temp_account_move ()
        INHERITS (account_move) ON COMMIT DROP;
        INSERT INTO temp_account_move SELECT move.*
        FROM ONLY account_move move
        LEFT JOIN ONLY account_move reversal
        ON reversal.reversed_entry_id = move.id
        --new line journals
        LEFT JOIN ONLY account_journal journal
        ON journal.id = move.journal_id
        WHERE reversal.id IS NULL AND move.asset_id IS NOT NULL
        AND move.company_id in %(company_ids)s
        --new condition journals
        and journal.accounting in %(accounting)s;

        SELECT asset.id as asset_id,
            asset.parent_id as parent_id,
            asset.name as asset_name,
            asset.value_residual as asset_value,
            asset.original_value as asset_original_value,
            asset.first_depreciation_date as asset_date,
            asset.disposal_date as asset_disposal_date,
            asset.acquisition_date as asset_acquisition_date,
            asset.method as asset_method,
            (
                account_move_count.count
                - CASE WHEN asset.prorata THEN 1 ELSE 0 END
            ) as asset_method_number,
            asset.method_period as asset_method_period,
            asset.method_progress_factor
            as asset_method_progress_factor,
            asset.state as asset_state,
            account.code as account_code,
            account.name as account_name,
            account.id as account_id,
            account.company_id as company_id,
            COALESCE(first_move.asset_depreciated_value,
            move_before.asset_depreciated_value, 0.0)
            as depreciated_start,
            COALESCE(first_move.asset_remaining_value,
            move_before.asset_remaining_value, 0.0)
            as remaining_start,
            COALESCE(last_move.asset_depreciated_value,
            move_before.asset_depreciated_value, 0.0)
            as depreciated_end,
            COALESCE(last_move.asset_remaining_value,
            move_before.asset_remaining_value, 0.0)
            as remaining_end,
            COALESCE(first_move.amount_total, 0.0) as depreciation,
            COALESCE(first_move.id, move_before.id)
            as first_move_id,
            COALESCE(last_move.id, move_before.id) as last_move_id
        FROM account_asset as asset
        LEFT JOIN account_account as account
        ON asset.account_asset_id = account.id
        LEFT JOIN (
            SELECT
                COUNT(*) as count,
                asset_id
            FROM temp_account_move
            WHERE asset_value_change != 't'
            GROUP BY asset_id
        ) account_move_count ON asset.id = account_move_count.asset_id

        LEFT OUTER JOIN (
            SELECT DISTINCT ON (asset_id)
                id,
                asset_depreciated_value,
                asset_remaining_value,
                amount_total,
                asset_id
            FROM temp_account_move m
            WHERE date >= %(date_from)s
            AND date <= %(date_to)s {where_account_move}
            ORDER BY asset_id, date, id DESC
        ) first_move ON first_move.asset_id = asset.id

        LEFT OUTER JOIN (
            SELECT DISTINCT ON (asset_id)
                id,
                asset_depreciated_value,
                asset_remaining_value,
                amount_total,
                asset_id
            FROM temp_account_move m
            WHERE date >= %(date_from)s
            AND date <= %(date_to)s {where_account_move}
            ORDER BY asset_id, date DESC, id DESC
        ) last_move ON last_move.asset_id = asset.id

        LEFT OUTER JOIN (
            SELECT DISTINCT ON (asset_id)
                id,
                asset_depreciated_value,
                asset_remaining_value,
                amount_total,
                asset_id
            FROM temp_account_move m
            WHERE date <= %(date_from)s {where_account_move}
            ORDER BY asset_id, date DESC, id DESC
        ) move_before ON move_before.asset_id = asset.id

        WHERE asset.company_id in %(company_ids)s
        AND asset.acquisition_date <= %(date_to)s
        AND (asset.disposal_date >= %(date_from)s
        OR asset.disposal_date IS NULL)
        AND asset.state not in ('model', 'draft')
        AND asset.asset_type = 'purchase'
        AND asset.active = 't'

        ORDER BY account.code;
        """.format(where_account_move=where_account_move)

        accounting = []
        if options.get('niif_colgap_asset', False):
            accounting = [
                option.get('id')
                for option in options['niif_colgap_asset']
                if option.get('selected')
            ]

        if not accounting:
            accounting = ['niif', 'fiscal', 'both']
        date_to = options['date']['date_to']
        date_from = options['date']['date_from']
        company_ids = tuple(t['id']
                            for t in self._get_options_companies(options))

        self.flush()
        self.env.cr.execute(
            sql, {'date_to': date_to, 'date_from': date_from,
                  'company_ids': company_ids, 'accounting': tuple(accounting)})
        results = self.env.cr.dictfetchall()
        self.env.cr.execute("DROP TABLE temp_account_move")
        return results
