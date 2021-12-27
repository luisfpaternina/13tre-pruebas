# -*- coding: utf-8 -*-

import csv
import base64
from io import StringIO, BytesIO
from odoo import models, fields, api, _


class AccountFlatFileSeverance(models.TransientModel):
    _inherit = 'account.flat.file.base'

    file_type = fields.Selection(
        selection_add=[('get_collect_data_payoffs', 'Layoffs')])

    file_extension = fields.Selection(
        string='File Extension',
        selection_add=[('csv', 'CSV')]
    )

    def _get_layoffs_lines(self):
        account_move_lines = self.env['account.move.line'].search([
            ['payment_id', '=', self.env.context['active_id']],
        ])

        return account_move_lines.filtered('debit')

    def _get_direction(self, partner):
        return '{0} {1}'.format(
            partner.street if partner.street else '-',
            partner.street2 if partner.street2 else '-')

    def _get_employee(self, line):
        return self.env['hr.employee'].search([
            ['address_id', '=', line.partner_id.id]
        ], limit=1)

    def _get_document_type(self, partner):
        return dict(
            partner._fields['document_type']._description_selection(
                self.env)).get(partner.document_type)

    def _get_worked_days(self, move_line):
        payslip = self.env['hr.payslip'].search([
            ['move_id', '=', move_line.move_id.id]
        ], limit=1)

        work_entry = self.env['hr.work.entry.type'].search([
            ['code', '=', 'WORK100']
        ], limit=1)

        # worked_days = next((line for line
        #                     in payslip.worked_days_line_ids
        #                     if line.work_entry_type_id.id == work_entry.id),
        #                    False)
        # if worked_days:
        #     return worked_days.number_of_days

        return 30

    def _get_file_layoffs(self):
        self.file_extension = 'csv'

        row_list = [
            [
                'TIPO_DOC',
                'NO_DOC',
                'NOMBRES',
                'APELLIDOS',
                'COD_ADMCESANTIAS',
                'SALARIO',
                'VALOR_CESANTIAS',
                'DIAS_TRABAJADOS',
                'TELEFONO',
                'DIRECCION',
                'CORREO'
            ]
        ]

        for line in self._get_layoffs_lines():
            partner = line.partner_id
            employee = self._get_employee(line)
            contract = employee.contract_id

            email = (partner.email
                     if partner.email else employee.work_email)

            row_list.append([
                self._get_document_type(partner),
                partner.number_identification,
                employee.names,
                employee.surnames,
                employee.layoffs.code,
                str(contract.wage),
                line.debit,
                self._get_worked_days(line),
                partner.phone if partner.phone else '',
                self._get_direction(partner),
                email
            ])

        file = StringIO()
        csv.writer(file, dialect='excel', delimiter=',').writerows(row_list)

        return file.getvalue().encode('utf-8')

    def get_collect_data_payoffs(self):
        return self._get_file_layoffs()
