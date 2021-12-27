# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AccountMoveColgap(models.Model):
    _inherit = 'account.move'

    colgap = fields.Boolean(
        string='Colgap',
    )

    def _depreciate_colgap(self):
        for move in self.filtered(lambda m: m.asset_id and m.colgap):
            asset = move.asset_id
            if asset.state in ('open', 'paused'):
                print("_depreciate_colgap************", move.colgap)
                asset.value_residual_colgap -= abs(sum(move.line_ids.filtered(
                    lambda l: l.account_id ==
                    asset.account_depreciation_colgap_id
                ).mapped('balance')))
            elif asset.state == 'close':
                asset.value_residual_colgap -= abs(sum(move.line_ids.filtered(
                    lambda l: l.account_id !=
                    asset.account_depreciation_colgap_id
                ).mapped('balance')))
            else:
                raise UserError(_('You cannot post a depreciation'
                                  ' on an asset in this state: %s') % dict(
                    self.env['account.asset']._fields[
                        'state'].selection)[asset.state])

    def _depreciate(self):
        for move in self.filtered(lambda m: m.asset_id and not m.colgap):
            asset = move.asset_id
            if asset.state in ('open', 'paused'):
                asset.value_residual -= abs(sum(move.line_ids.filtered(
                    lambda l: l.account_id == asset.account_depreciation_id
                ).mapped('balance')))
            elif asset.state == 'close':
                asset.value_residual -= abs(sum(move.line_ids.filtered(
                    lambda l: l.account_id != asset.account_depreciation_id
                ).mapped('balance')))
            else:
                raise UserError(_('You cannot post a depreciation'
                                  ' on an asset in this state: %s') % dict(
                    self.env['account.asset']._fields[
                        'state'].selection)[asset.state])
        self._depreciate_colgap()


class AccountMoveLineNIIF(models.Model):
    _inherit = 'account.move.line'

    colgap = fields.Boolean(
        string='Colgap',
    )
