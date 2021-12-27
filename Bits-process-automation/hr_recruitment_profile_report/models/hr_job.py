# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class HrJob(models.Model):
    _inherit = 'hr.job'

    document_version_ids = fields.One2many(
        'document.version.control', 'job_id', string='Document Version')

    def _get_control_version(self):
        result = self.env['document.version.control'].search(
            [('job_id', '=', self.id)])
        return result

    def _get_order_version_document(self, result):
        document_version_ids = result.read([])
        document_version_dict = sorted(
            document_version_ids,
            key=lambda document_version: document_version['version'],
            reverse=True)
        return document_version_dict

    def _get_last_version_document(self):
        format_version = '0.0.0'
        result = self._get_control_version()
        if result:
            version_record = self._get_order_version_document(result)
            format_version = version_record[0].get('version')
        return format_version

    def _get_conversion_date(self, version_data):
        months = (
            "Enero", "Febrero", "Marzo", "Abri", "Mayo", "Junio", "Julio",
            "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
        )

        str_last_version = version_data[0].get(
            'version_date').strftime('%b %d %Y')
        if self.env.user.lang == 'es_CO':
            date_last_version = version_data[0].get('version_date')
            day = date_last_version.day
            month = months[date_last_version.month-1]
            year = date_last_version.year
            str_last_version = "{} {} de {}".format(month, day, year)
        return str_last_version

    def _get_format_date_document(self):
        str_last_version = "00-00-00"
        result = self._get_control_version()
        if result:
            version_data = self._get_order_version_document(result)
            str_last_version = self._get_conversion_date(version_data)
        return str_last_version
