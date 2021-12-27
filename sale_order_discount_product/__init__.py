# -*- coding: utf-8 -*-

import logging
from . import models

from odoo import api, SUPERUSER_ID
_logger = logging.getLogger(__name__)


def _post_init_hook_sale_order_discount_product(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    group_approver_general_freight = env.ref(
        'freight_approval.group_manager_sale_approval',
        raise_if_not_found=True
    )
    new_group_freight_approval = env.ref(
        'sale_order_discount_product.group_manager_freight_approval'
    )

    if group_approver_general_freight:
        users_to_new_group = []
        for user in group_approver_general_freight.users:
            users_to_new_group.append(user.id)
        new_group_freight_approval.update({
            'users': [
                (6, 0, users_to_new_group)
            ]
        })
        group_approver_general_freight.unlink()


def uninstall_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    group_approver_general_freight = env.ref(
        'freight_approval.group_manager_sale_approval',
        raise_if_not_found=False
    )

    if not group_approver_general_freight:
        modules = env['ir.module.module'].search(
            [
                ('state', '=', 'installed'),
                ('name', '=', 'freight_approval')
            ]
        )
        if modules:
            modules[0].button_upgrade()
