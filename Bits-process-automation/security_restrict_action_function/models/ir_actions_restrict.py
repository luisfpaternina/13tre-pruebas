# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class IrRestrictActions(models.Model):
    _name = 'ir.actions.restrict'

    name = fields.Char(string='name', required=True)
    model = fields.Char(string='Model', required=True)
    action_name = fields.Char(string="Action Name", required=True)
    action_code = fields.Char(string="Action Code", required=True)
    description = fields.Char(string="Description")
    message_show = fields.Char(string="Message to Show", required=True)
    groups_access_ids = fields.Many2many('res.groups',
                                         'actions_groups_access_rel',
                                         string="Groups Access")
    active = fields.Boolean(string="Active", default=True)

    def validate_user_groups_by_id(self, group_id):
        result = self.env['res.users'].search([
            ('groups_id', 'in', (group_id)),
            ('id', '=', self.env.user.id)])
        return result

    def validate_user_groups(self):
        for record in self:
            permission_granted = False
            if record.groups_access_ids:
                dict_groups = record.groups_access_ids.get_external_id()
                for group in dict_groups.items():
                    if group[1] and record.user_has_groups(group[1]):
                        permission_granted = True
                    if record.validate_user_groups_by_id(group[0]):
                        permission_granted = True
                if not permission_granted:
                    raise ValidationError(record.message_show)
