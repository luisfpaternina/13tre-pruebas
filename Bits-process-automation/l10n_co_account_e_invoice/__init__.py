# -*- coding: utf-8 -*-
import logging
from . import models
from . import wizard

from odoo import api, SUPERUSER_ID
_logger = logging.getLogger(__name__)


def _post_init_hook_l10n_co_account_e_invoice(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    chart_template = env.ref(
        'l10n_co.l10n_co_chart_template_generic', raise_if_not_found=False)

    if chart_template:
        companies = env['res.company'].search(
            [('chart_template_id', '=', chart_template.id)])
        for company in companies:
            env['account.tax.template']._configure_l10n_co_account_tax_data(
                company)
