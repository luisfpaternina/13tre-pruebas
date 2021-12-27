# -*- coding: utf-8 -*-

import csv

from datetime import datetime, timedelta
from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta
from odoo.modules.module import get_module_resource


class AccountFlatFileDavivienda(models.TransientModel):
    _inherit = "account.flat.file.base"

    default_character = '0'
    transfers_value = 0
    total_transfers = ""
    create_date_format = ""
    create_hour = ""
    dateTime = datetime.now() - timedelta(hours=5)

    document_type_data = {
        '12': '04',
        '13': '01',
        '22': '02',
        '41': '5',
        '31': '03'
    }
    account_type_data = {
        "current_account": "CC",
        "saving": "CA",
        "dp": "DP"
    }

    service_code = fields.Selection([
        ('NOMI', 'Payment of Payroll'),
        ('PROV', 'Payment of Providers'),
        ('REND', 'Payment of Yield'),
        ('SUBS', 'Payment of subsidies'),
        ('SUBV', 'Payment of housing subsidies'),
        ('FOND', 'Payment of Employees Fund')
    ], string="Service Code")
    subservice_code = fields.Selection([
        ('NOMI', 'Payroll Service'),
        ('PROV', 'Providers Service')
    ], string="Subservice Code")

    def _get_data_rc_fields(self):
        return [
            # Identificador del registro de control
            {'type': 'S', 'long': '2',
                'method': 'compute_default_data',
                'default_value': 'RC'},
            # Nit de la empresa
            {'type': 'N', 'long': '16',
                'method': 'get_nit_company',
                'default_value': ''},
            # Código del servicio
            {'type': 'S', 'long': '4',
                'method': 'get_self_data',
                'default_value': 'service_code'},
            # Código del subservicio
            {'type': 'S', 'long': '4',
                'method': 'get_self_data',
                'default_value': 'subservice_code'},
            # Cuenta de la empresa
            {'type': 'N', 'long': '16',
                'method': 'get_self_data',
                'default_value': 'account_debit'},
            # Tipo de cuenta
            {'type': 'S', 'long': '2',
                'method': 'get_account_type',
                'default_value': ''},
            # Código del banco (000051) es el del BANCO DAVIVIENDA
            {'type': 'N', 'long': '6',
                'method': 'compute_default_data',
                'default_value': '000051'},
            # Valor total de los traslados
            {'type': 'N', 'long': '18',
                'method': 'get_self_data',
                'default_value': 'transfers_value'},
            # Número total de los traslados
            {'type': 'N', 'long': '6',
                'method': 'get_self_data',
                'default_value': 'total_transfers'},
            # Fecha proceso (AAAAMMDD)
            {'type': 'N', 'long': '8',
                'method': 'get_self_data',
                'default_value': 'create_date_format'},
            # Hora de proceso (HHMMSS)
            {'type': 'N', 'long': '6',
                'method': 'get_self_data',
                'default_value': 'create_hour'},
            # Código del operador (Enviar campo con ceros)
            {'type': 'S', 'long': '4',
                'method': 'compute_default_data',
                'default_value': ''},
            # Código no procesado (Enviar campo con 9999)
            {'type': 'N', 'long': '4',
                'method': 'compute_default_data',
                'default_value': '9999'},
            # Fecha Generación (Enviar campo con ceros)
            {'type': 'N', 'long': '8',
                'method': 'compute_default_data',
                'default_value': ''},
            # Hora Generación (Enviar campo con ceros)
            {'type': 'N', 'long': '6',
                'method': 'compute_default_data',
                'default_value': ''},
            # Indicador de inscripción (Enviar campo con ceros)
            {'type': 'N', 'long': '2',
                'method': 'compute_default_data',
                'default_value': ''},
            # Tipo de identificación
            {'type': 'N', 'long': '2',
                'method': 'get_company_document_type',
                'default_value': ''},
            # Número del Cliente asignado por
            # Davivienda (Enviar campo con ceros)
            {'type': 'N', 'long': '12',
                'method': 'compute_default_data',
                'default_value': ''},
            # Oficina de Recaudo (Enviar campo con ceros)
            {'type': 'N', 'long': '4',
                'method': 'compute_default_data',
                'default_value': ''},
            # Campo futuro (Enviarcampo con ceros)
            {'type': 'N', 'long': '40',
                'method': 'compute_default_data',
                'default_value': ''}
        ]

    def _get_data_tc_fields(self):
        return [
            # Enviar las letras TR al inicio del registro
            # (Tipo de registro de Traslados)
            {'type': 'S', 'long': '2',
                'method': 'compute_default_data',
                'default_value': 'TR'},
            # Nit del producto ó servicio destino
            {'type': 'N', 'long': '16',
                'method': 'get_number_identification',
                'default_value': ''},
            # Referencia (Enviar campo con ceros)
            {'type': 'N', 'long': '16',
                'method': 'compute_default_data',
                'default_value': ''},
            # Producto ó servicio destino u origen
            {'type': 'N', 'long': '16',
                'method': 'get_number_account',
                'default_value': ''},
            # Tipo de producto ó servicio:
            {'type': 'N', 'long': '2',
                'method': 'get_partner_account_type',
                'default_value': ''},
            # Código del Banco 000051: BANCO DAVIVIENDA
            {'type': 'N', 'long': '6',
                'method': 'compute_default_data',
                'default_value': '51'},
            # Valor a cargar
            {'type': 'N', 'long': '18',
                'method': 'get_debit',
                'default_value': ''},
            # Talón: Empresa (Enviar inicialmente en Ceros)
            {'type': 'N', 'long': '6',
                'method': 'compute_default_data',
                'default_value': ''},
            # Tipo de identificación
            {'type': 'N', 'long': '2',
                'method': 'get_document_type',
                'default_value': ''},
            # Validar traslados a ACH(Enviar campo con 1)
            {'type': 'N', 'long': '1',
                'method': 'compute_default_data',
                'default_value': '1'},
            # Resultado del proceso que asume los valores
            # (Enviar campo con 9999)
            {'type': 'N', 'long': '4',
                'method': 'compute_default_data',
                'default_value': '9999'},
            # Mensaje de Respuesta (Enviar campo con ceros)
            {'type': 'N', 'long': '40',
                'method': 'compute_default_data',
                'default_value': ''},
            # Valor acumulado del cobro (Enviar campo con ceros) (2 decimales)
            {'type': 'N', 'long': '18',
                'method': 'compute_default_data',
                'default_value': ''},
            # Fecha de Aplicación (Enviar campo con ceros)
            {'type': 'N', 'long': '8',
                'method': 'compute_default_data',
                'default_value': ''},
            # Oficina deRecaudo (Enviar campo con ceros)
            {'type': 'N', 'long': '4',
                'method': 'compute_default_data',
                'default_value': ''},
            # Motivo (Enviar campo con ceros)
            {'type': 'N', 'long': '4',
                'method': 'compute_default_data',
                'default_value': ''},
            # (Enviar campo con ceros)
            {'type': 'N', 'long': '7',
                'method': 'compute_default_data',
                'default_value': ''}
        ]

    def get_nit_company(self, long, data):
        company_id = self.partner_id.id
        partner_data = self.env['res.partner'].search(
            [('id', '=', company_id)],
            limit=1)
        number_identification_partner = partner_data.number_identification
        if (number_identification_partner
                and number_identification_partner.find("-") > 0):
            number_identification_partner = (
                number_identification_partner.replace("-", ""))
        result = self.add_default_character(long,
                                            number_identification_partner)
        return result

    def get_company_document_type(self, long, data):
        company_id = self.partner_id.id
        partner_data = self.env['res.partner'].search(
            [('id', '=', company_id)],
            limit=1)
        partner_document_type = str(partner_data.document_type)
        result = self.document_type_data.get(partner_document_type, '00')
        result = self.add_default_character(long, result)
        return result

    def get_number_identification(self, long, data):
        partner_id = data.partner_id.id
        partner_data = self.env['res.partner'].search(
            [('id', '=', partner_id)],
            limit=1)
        result = partner_data.number_identification
        if result and result.find("-") > 0:
            result = result.replace("-", "")
        result = self.add_default_character(long, result)
        return result

    def get_document_type(self, long, data):
        partner_id = data.partner_id.id
        partner_data = self.env['res.partner'].search(
            [('id', '=', partner_id)],
            limit=1)
        document_type = str(partner_data.document_type)
        result = self.document_type_data.get(document_type, '00')
        result = self.add_default_character(long, result)
        return result

    def get_account_type(self, long, data):
        result = self.account_type_data.get(self.account_type, '')
        result = self.add_default_character(long, result)
        return result

    def get_partner_account_type(self, long, data):
        partner_id = data.partner_id.id
        partner_data = self.env['res.partner'].search(
            [('id', '=', partner_id)],
            limit=1)
        account_type = partner_data.bank_ids[0].account_type
        result = self.account_type_data.get(account_type, '')
        result = self.add_default_character(long, result)
        return result

    def get_debit(self, long, data):
        debit = str("%.2f" % data[0].debit)
        debit = self.decimalValidator(debit)
        result = self.add_default_character(long, debit)
        return result

    def get_number_account(self, long, data):
        partner_id = data.partner_id.id
        partner_data = self.env['res.partner'].search(
            [('id', '=', partner_id)],
            limit=1)
        number_account = partner_data.bank_ids[0].acc_number
        result = self.add_default_character(long, number_account)
        return result

    def dateCreator(self):
        dateTime = self.dateTime
        dateValidator = self.dateValidator
        self.create_hour = (
            dateValidator(dateTime.hour) +
            dateValidator(dateTime.minute) + dateValidator(dateTime.second))
        self.create_date_format = (dateValidator(
            dateTime.year) + dateValidator(dateTime.month) +
            dateValidator(dateTime.day))

    def dateValidator(self, value):
        value = str(value)
        if len(value) < 2:
            value = "0" + value
        return value

    def decimalValidator(self, value):
        result = value.replace(".", "")
        return result

    def get_self_data(self, long, data):
        self_attr = getattr(
            self, data)
        result = self.add_default_character(long, self_attr)
        return result

    def add_default_character(self, long, value):
        longValue = len(str(value))
        diff_long = int(long) - int(longValue)
        default_character = self.default_character
        default_characters = ''.join(
            [char*int(diff_long) for char in default_character])
        result = str(default_characters) + str(value)
        return result

    def compute_default_data(self, long, default_value):
        value = ''
        if default_value != '':
            value = self.add_default_character(long, default_value)
        else:
            default_character = self.default_character
            value = ''.join([char*int(long) for char in default_character])
        return value

    def _get_header_file_davivienda(self):
        header = ''
        header = self._get_line_data('_get_data_rc_fields', '')
        return bytes(header, 'utf8')

    def _get_body_file_davivienda(self):
        lines = self.env['account.move.line']
        body = ''
        transfers_value = 0
        if self.env.context['payment_type'] == "Supplier":
            payments = self.env['account.payment'].search([
                (
                    'account_collective_payments_supplier_id',
                    '=', self.env.context['active_id'])
            ])
            for payment in payments:
                lines += payment.move_line_ids.filtered('debit')
        else:
            payment = self.env['account.payment'].browse(
                self.env.context['active_id'])
            lines = payment.move_line_ids.filtered('debit')
        self.total_transfers = len(lines)
        for line in lines:
            body += self._get_line_data('_get_data_tc_fields', line)
            transfers_value = float(transfers_value) + float(line[0].debit)
        self.transfers_value = self.decimalValidator(
            str("%.2f" % transfers_value))
        return bytes(
            body, 'utf8')

    def _get_line_data(self, parent_method, data):
        fields_method = getattr(
            self, parent_method)
        _fields = fields_method()
        row_data = ''
        line = ''
        for row in _fields:
            func_name = row.get('method', '')
            long = row.get('long', '')
            if (func_name == "compute_default_data" or
                    func_name == "get_self_data"):
                send = row.get('default_value', '')
            else:
                send = data
            self_method = getattr(
                self, func_name)
            row_data += self_method(long, send)
        line += row_data + "\n"
        return line

    def get_collect_data_bank(self):
        if self.bank_id.bic == '51':
            self.dateCreator()
            body = self._get_body_file_davivienda()
            header = self._get_header_file_davivienda()
            return header + body
        result = super(AccountFlatFileDavivienda, self).get_collect_data_bank()
        return result
