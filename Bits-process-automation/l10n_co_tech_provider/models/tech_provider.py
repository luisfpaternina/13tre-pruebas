# -*- coding: utf-8 -*-

import csv
import datetime
import base64
from io import BytesIO
from odoo import models, fields, api
from odoo.addons.bits_api_connect.models.adapters.builder_file_adapter\
    import BuilderToFile

from odoo.addons.bits_api_connect.models.connections.api_connection_facturaxion\
    import ApiConnectionRequestFacturaxionPayroll, ApiConnectionRequestFacturaxion


class TechProvider(models.Model):
    _name = 'l10n_co.tech.provider'
    _description = 'l10n_co_tech_provider'

    name = fields.Char(required=True)
    code = fields.Char(required=True, size=3)
    description = fields.Text()
    username = fields.Char()
    password = fields.Char()
    connection_url = fields.Char()
    connection_type = fields.Selection(
        [('soap', 'SOAP'), ('rest', 'REST')]
    )
    file_extension = fields.Selection(
        string='File Extension',
        selection=[('txt', 'TXT'), ('xml', 'XML')],
        required=True,
        default='txt'
    )
    file_separator = fields.Char(
        required=True,
        default='|'
    )
    file_filename = fields.Char('File Names')
    file_binary = fields.Binary(string='File')
    num_of_days_to_validate = fields.Integer(
        string="Num of days to validate acknowledgment",
        required=True,
        default=3
    )
    num_doc_attachs = fields.Integer(string="Number Doc Attachs")
    maximum_megabytes = fields.Integer()

    line_ids = fields.One2many(
        'l10n_co.tech.provider.line',
        'tech_provider_id',
        string='Lines')

    url_upload = fields.Char()
    url_download = fields.Char()
    is_test = fields.Boolean(
        string="Test mode",
        default=True
    )

    connection_adapter = fields.Char()
    file_adapter = fields.Char()

    _type = fields.Selection([('account', 'Account')], default='account')
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        default=lambda self: self.env.company,
    )
    property_company_id = fields.Many2one(
        comodel_name='res.company',
        company_dependent=True,
        string='Company',
    )

    def get_collect_data(self):
        return b'Information File'

    def get_data_file(self):
        collect_data = self.get_collect_data()
        file_output = BytesIO(collect_data)
        file_output.seek(0)
        return file_output.read()

    def action_test_connection(self):
        test_class = ApiConnectionRequestFacturaxionPayroll(
            self.env.company.partner_id,
            self.username,
            self.password,
            self.url_upload
            )
        pass
