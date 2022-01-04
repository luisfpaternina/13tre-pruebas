from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    call_token = fields.Char(
        string="RingOver API Key",
        config_parameter='call.register.token',
        required=True
    )
    endpoint_calls = fields.Char(string="Calls Endpoint",
                                 default='https://public-api.ringover.com/v2/calls',
                                 config_parameter='call.endpoint', required=True)

    last_cdr_id = fields.Integer(
        string='Last CDR ID', config_parameter='call.last_cdr_id', default=0)

