# -*- coding: utf-8 -*-

import csv
import math
import base64
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from ast import literal_eval

from odoo import models, fields, api, _
import logging
_logger = logging.getLogger(__name__)


class AccountFlatFileParafiscal(models.TransientModel):
    _inherit = "account.flat.file.base"

    date_from = fields.Date(
        string='Date From',
        default=datetime.now().strftime('%Y-%m-01')
    )
    date_to = fields.Date(
        string='Date To',
        default=str(datetime.now() + relativedelta(
            months=+1, day=1, days=-1))[:10]
    )
    struct_ids = fields.Many2many(
        string='Salary Structure',
        comodel_name='hr.payroll.structure',
        relation='structure_flat_file_rel',
    )

    def _get_payslip_by_period(self):
        domain = [('date_from', '>=', self.date_from),
                  ('date_to', '<=', self.date_to)]
        if self.struct_ids:
            domain += [('struct_id', 'in', self.struct_ids.ids)]
        payslip_ids = self.env['hr.payslip'].search(domain)
        return payslip_ids

    def _get_body_file(self):
        body = ''
        header = ''
        total = []
        sequence = 1
        payslip_ids = self._get_payslip_by_period()
        
        _logger.error(type(payslip_ids))
        _logger.error(len(payslip_ids))
        #_logger.error(payslip_ids)
        new_list = []
        for payslip in payslip_ids:
            print(payslip.state)
            print(payslip.id)
            if payslip.state == 'done':
                print(type(payslip_ids))
                new_list.append(payslip)
        payslip_ids = new_list
        if len(payslip_ids) == 0:
            return bytes(body, 'utf8'), total
        localarray = []
        _fields = self._get_data_fields()
        print(type(_fields))
        for field in _fields:
            print(type(field))
        for payslip_id in payslip_ids:
            row_data = ''
            basic_info = []
            localdict = dict()
            lines = payslip_id.line_ids.filtered(
                lambda line: line.code == 'BASIC')
            print("******lines*****", lines)
            total.append(sum([line.total for line in lines]))
            for row in _fields:
                func_name = row.get('field', '')
                self_method = getattr(
                    self, 'compute_field_%s' % (func_name))
                str_data = self_method(
                    row, payslip_id, sequence, localdict)
                row_data += str_data
                basic_info.append(str_data)
            aditional = self._generate_payroll_news_lines(
                row, payslip_id, sequence, localdict, basic_info)
            localarray.append(basic_info)
            len_adi = len(aditional)
            localarray += aditional if len_adi > 0 else []
            sequence += len_adi + 1 if len_adi > 0 else 1

        if self.file_extension == 'csv':
            row_data = '\n'.join([",".join(item) for item in localarray])
            for row in _fields:
                func_name = row.get('field', '')
                label = row.get('label', '')
                header += func_name + ':' + label + ','
            body += header + "\n" + row_data + "\n"
        else:
            row_data = '\n'.join(["".join(item) for item in localarray])
            body += row_data + "\n"
        return bytes(body, 'utf8'), total

    def _get_body_file_parafiscal(self):
        if self.env.context.get('flat_file_payroll', False):
            print("validando contexto*******")
            return self._get_body_file()
        return super(AccountFlatFileParafiscal,
                     self)._get_body_file_parafiscal()

    def export_flat_file(self):
        get_data = self.get_data_flat_file()
        if self.env.context.get('flat_file_payroll', False):
            self.partner_id = self.env.company.partner_id
            print("****////*/**/**/**/*/*/", self.partner_id)
            self.write({
                'file_filename': 'flat_file.{0}'.format(self.file_extension),
                'file_binary': base64.b64encode(get_data)
            })
            return {
                'context': self.env.context,
                'name': _("Flat File Parafiscales"),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'account.flat.file.base',
                'res_id': self.id,
                'view_id': self.env.ref(
                    'hr_payroll_flat_file_parafiscal.'
                    'hr_payroll_flat_file_parafiscal_form').id,
                'type': 'ir.actions.act_window',
                'target': 'new',
            }
        return super(AccountFlatFileParafiscal, self).export_flat_file()
