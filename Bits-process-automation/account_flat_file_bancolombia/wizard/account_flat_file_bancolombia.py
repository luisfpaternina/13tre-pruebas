from odoo import models, fields, api, _
from datetime import datetime, date
import calendar


class AccountFlatFileBancolombia(models.TransientModel):
    _inherit = 'account.flat.file.base'
    _description = "Flat File Bancolombia"
    default_character = '0'
    line_body = []
    lines_body = []
    total_lines = ''
    Opc = {
        '1': 'Fax',
        '2': 'Email',
        '3': 'Free text'
    }
    Documents_type = {
        '12': '4',  # Tarjeta de identidad
        '13': '1',  # Cédula de ciudadanía
        '22': '2',  # Cédula de extranjeria
        '41': '5',  # Pasaporte
        '31': '3',  # NIT
        'OT': ''  # Otros
    }
    Concept_draft = {
        '1': '''Pago a Prestadores de Servicios de Salud,
                 proveedores de insumos y/o suministros relacionados
                 con la atención en salud.''',
        '2': ''''Pago a Prestadores de Servicios de Salud,
                  proveedores de insumos y/o suministros relacionados
                  con la atención en salud por servicios extraordinarios
                  en salud''',
        '3': 'Devolución de Aportes',
        '4': 'Prestaciones económicas',
        '5': 'Gastos Administrativos propios de la EPS',
        '6': ''''Costo financiero convenio bancario de recaudo y
                  pago''',
        '7': 'Pago al Operador de información'
    }
    Month_homologation = {
        'Jan': 'ENE',
        'Feb': 'FEB',
        'Mar': 'MAR',
        'Apr': 'ABR',
        'May': 'MAY',
        'Jun': 'JUN',
        'Jul': 'JUL',
        'Aug': 'AGO',
        'Sep': 'SEP',
        'Oct': 'OCT',
        'Nov': 'NOV',
        'Dec': 'DIC'
    }
    Month_homologation_2 = {
        'Jan': 'ENERO',
        'Feb': 'FEBRERO',
        'Mar': 'MARZO',
        'Apr': 'ABRIL',
        'May': 'MAYO',
        'Jun': 'JUNI',
        'Jul': 'JULIO',
        'Aug': 'AGOSTO',
        'Sep': 'SEPTIEMBRE',
        'Oct': 'OCTUBRE',
        'Nov': 'NOVIEMBRE',
        'Dec': 'DICIEMBRE'
    }
    place_to_pay = fields.Selection([
        ('S', 'Abono a Cuenta'),
        ('1', 'Cheque de Gerencia')
    ], string="Place to pay")

    transaction_type = fields.Selection(selection_add=[
        ('25', 'Pago en Efectivo'),
        ('26', 'Pago en Cheque'),
        ('27', 'Abono a cuenta corriente'),
        ('37', 'Abono a cuenta ahorros'),
    ], string="Transaction Type")
    Bank_account_approval = {
        'current_account': 'D',
        'saving': 'S'
    }
    class_transactions = {
        'PAGO DE NOMINA': '225',
    }

    # header
    def get_batch_control_registry(self):
        return [
            # Tipo registro
            {'type': 'N', 'lng': '1',
                'method': 'get_record_type',
                'default_value': '1',
                'filled': '0',
                'side': 'R'},
            # Nit entidad Originadora
            {'type': 'N', 'lng': '15',
                'method': 'get_origin_company_nit',
                'default_value': '',
                'filled': '0',
                'side': 'R'},
            # Aplicación
            {'type': 'S', 'lng': '1',
                'method': 'get_record_type',
                'default_value': ' ',
                'filled': ' ',
                'side': 'R'},
            # Filler
            {'type': 'S', 'lng': '15',
                'method': 'get_record_type',
                'default_value': ' ',
                'filled': ' ',
                'side': 'R'},
            # Clase de transacción
            {'type': 'S', 'lng': '3',
                'method': 'get_contained_class_transactions',
                'default_value': '',
                'filled': '0',
                'side': 'R'},
            # Descripción propósito transacciones
            {'type': 'S', 'lng': '10',
                'method': 'get_description_purpose_transactions',
                'default_value': '',
                'filled': ' ',
                'side': 'L'},
            # Fecha Transmisión de lote
            {'type': 'S', 'lng': '8',
                'method': 'get_aplication_date',
                'default_value': '',
                'filled': '0',
                'side': 'R'},
            # Secuencia envio de lotes ese día
            {'type': 'S', 'lng': '2',
                'method': 'get_sequence_batch_sending_that_day',
                'default_value': 'A',
                'filled': ' ',
                'side': 'L'},
            # Fecha aplicación transacciones
            {'type': 'S', 'lng': '8',
                'method': 'get_aplication_date',
                'default_value': '',
                'filled': '0',
                'side': 'R'},
            # Número de registros
            {'type': 'N', 'lng': '6',
                'method': 'get_records_number_details_documents',
                'default_value': '',
                'filled': '0',
                'side': 'R'},
            # Sumatoria de débitos
            {'type': 'N', 'lng': '17',
                'method': 'get_add_debits',
                'default_value': '',
                'filled': '0',
                'side': 'R'},
            # Sumatoria de créditos
            {'type': 'N', 'lng': '17',
                'method': 'get_add_credits',
                'default_value': '',
                'filled': '0',
                'side': 'R'},
            # Cuenta cliente a debitar
            {'type': 'N', 'lng': '11',
                'method': 'get_customer_account_debit',
                'default_value': '',
                'filled': '0',
                'side': 'R'},
            # Tipo de cuenta cliente a debitar
            {'type': 'S', 'lng': '1',
                'method': 'get_type_customer_account_debit',
                'default_value': '',
                'filled': '0',
                'side': 'R'}
        ]

    # body
    def get_transaction_detail_record(self):
        return [
            # Tipo registro
            {'type': 'N', 'lng': '1',
                'method': 'get_record_type_transaction_detail_records',
                'default_value': '6',
                'filled': '0',
                'side': 'R'},
            # Nit beneficiario
            {'type': 'N', 'lng': '15',
                'method': 'get_beneficiary_nit',
                'default_value': '',
                'filled': ' ',
                'side': 'L'},
            # Nombre del beneficiario
            {'type': 'S', 'lng': '30',
                'method': 'get_name_beneficiary',
                'default_value': '',
                'filled': ' ',
                'side': 'L'},
            # VALIDAR!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            # Banco cuenta del beneficiario (destino)
            {'type': 'N', 'lng': '9',
                'method': 'get_bank_account_beneficiary',
                'default_value': '',
                'filled': '0',
                'side': 'R'},
            # Número cuenta del beneficiario
            {'type': 'N', 'lng': '17',
                'method': 'get_number_benficiary_account',
                'default_value': '',
                'filled': ' ',
                'side': 'L'},
            # Indicador Lugar de pago
            {'type': 'N', 'lng': '1',
                'method': 'get_record_type',
                'default_value': '',
                'filled': ' ',
                'side': 'L'},
            # Tipo de transacción
            {'type': 'N', 'lng': '2',
                'method': 'get_transaction_type',
                'default_value': '',
                'filled': '0',
                'side': 'R'},
            # Valor transacción
            {'type': 'N', 'lng': '17',
                'method': 'get_transaction_value',
                'default_value': '',
                'filled': '0',
                'side': 'R'},
            # Fecha aplicación
            {'type': 'N', 'lng': '8',
                'method': 'get_record_type',
                'default_value': '',
                'filled': '0',
                'side': 'L'},
            # Referencia
            {'type': 'S', 'lng': '21',
                'method': 'get_reference',
                'default_value': '',
                'filled': ' ',
                'side': 'L'},
        ]

    # Create default character for string
    def create_default_string_char(self, lng, default_value,
                                   value, fill, side):
        lng = int(lng)

        if (default_value != "") and len(default_value) < lng:
            lng -= len(default_value)
            default_characters = default_value.join(
                [char*lng for char in fill])
            return (str(default_characters) + str(default_value)
                    if side == "R" else str(default_value) +
                    str(default_characters))
        elif len(default_value) == lng:
            return default_value
        else:
            if (lng - len(str(value))) < 0:
                return value[:lng]
            else:
                lng -= len(str(value))
            default_characters = ''.join([char*lng for char in fill])
            return (str(default_characters) + str(value)
                    if side == "R" else str(value) +
                    str(default_characters))

    # create lines flat file
    def create_line_data(self, parent_method):
        fields_method = getattr(
            self, parent_method)
        _fields = fields_method()
        row_data = ''
        line = ''
        for row in _fields:
            func_name = row.get('method', '')
            lng = row.get('lng', '')
            default_value = row.get('default_value', '')
            fill = row.get('filled', '')
            side = row.get('side', '')
            self_method = getattr(
                self, func_name)
            row_data += self_method(lng, default_value, fill, side)
        line += row_data + "\n"
        return line

    # header
    def get_header_file_bancolombia(self):
        self.lines_body = self.env['account.move.line']
        if self.env.context['payment_type'] == "Supplier":
            payments = self.env['account.payment'].search([(
                'account_collective_payments_supplier_id',
                '=', self.env.context['active_id'])
            ])
            print(payments.read([]))
            for payment in payments:
                self.lines_body += payment.move_line_ids
        else:
            payment = self.env['account.payment'].browse(
                self.env.context['active_id'])
            self.lines_body = payment.move_line_ids
        self.total_lines = len(self.lines_body.filtered('debit'))
        header = self.create_line_data('get_batch_control_registry')
        return bytes(
            header, 'utf8')

    # body
    def get_body_file_bancolombia(self):
        body = ''
        transfers_value = 0
        for line in self.lines_body.filtered('debit'):
            self.line_body = line
            body += self.create_line_data('get_transaction_detail_record')
            transfers_value = float(transfers_value) + float(line[0].debit)
        self.transfers_value = str("%.2f" % transfers_value)
        return bytes(
            body, 'utf8')

    # header's methods

    def get_aplication_date(self, lng, default_value, fill, side):
        date = self.application_date
        value = (date.strftime("%Y") +
                 self.dateValidator(date.strftime("%m")) +
                 self.dateValidator(date.strftime("%d")))
        return (self.create_default_string_char(lng, default_value,
                                                value, fill, side))

    def dateValidator(self, value):
        value = str(value)
        value = ("0" + value) if len(value) < 2 else value
        return value

    def get_record_type(self, lng, default_value, fill, side):
        value = ''
        return self.create_default_string_char(lng, default_value,
                                               value, fill, side)

    def get_origin_company_nit(self, lng, default_value, fill, side):
        value = ''
        value = self.partner_id.number_identification.replace(
            "-", "") if self.partner_id.number_identification else value
        return self.create_default_string_char(lng, default_value,
                                               value, fill, side)

    def get_contained_class_transactions(self, lng, default_value, fill, side):
        value = self.class_transactions.get("PAGO DE NOMINA", '')
        return self.create_default_string_char(lng, default_value,
                                               value, fill, side)

    def get_description_purpose_transactions(self, lng, default_value,
                                             fill, side):
        date = datetime.strptime(str(self.application_date), '%Y-%m-%d').month
        value = self.Month_homologation.get(calendar.month_abbr[date], '')
        return self.create_default_string_char(lng, default_value,
                                               value, fill, side)

    def get_sequence_batch_sending_that_day(self, lng, default_value,
                                            fill, side):
        value = ''
        return self.create_default_string_char(lng, default_value,
                                               value, fill, side)

    def get_records_number_details_documents(self, lng, default_value,
                                             fill, side):
        value = str(self.total_lines)
        return self.create_default_string_char(lng, default_value,
                                               value, fill, side)

    def get_add_debits(self, lng, default_value, fill, side):
        value = ''
        return self.create_default_string_char(lng, default_value,
                                               str(value), fill, side)

    def get_add_credits(self, lng, default_value, fill, side):
        value = 0
        for line in self.lines_body.filtered('credit'):
            value += float(line[0].credit)
        value = self.round_value(value)
        return self.create_default_string_char(lng, default_value,
                                               str(value), fill, side)

    def round_value(self, value):
        value = str(round(value, 2))
        value = value.split(".")
        value = value if len(value) > 1 else value.split(",")
        floatValue = value[1]
        floatValue = floatValue if len(floatValue) > 1 else floatValue + "0"
        value = value[0] + floatValue
        return value

    def get_customer_account_debit(self, lng, default_value, fill, side):
        value = self.account_debit
        return self.create_default_string_char(lng, default_value,
                                               value, fill, side)

    def get_type_customer_account_debit(self, lng, default_value, fill, side):
        value = self.Bank_account_approval.get(
            self.partner_id.bank_ids[0].account_type, '')
        return self.create_default_string_char(lng, default_value,
                                               value, fill, side)

    # body's methods
    def get_record_type_transaction_detail_records(self, lng, default_value,
                                                   fill, side):
        value = ''
        return self.create_default_string_char(lng, default_value,
                                               value, fill, side)

    def get_beneficiary_nit(self, lng, default_value, fill, side):
        value = str(self.line_body.partner_id.number_identification)
        return self.create_default_string_char(lng, default_value,
                                               value, fill, side)

    def get_name_beneficiary(self, lng, default_value, fill, side):
        value = str(self.line_body.partner_id.name)
        return self.create_default_string_char(lng, default_value,
                                               value, fill, side)

    def get_bank_account_beneficiary(self, lng, default_value, fill, side):
        partner = self.line_body.partner_id
        value = partner.bank_ids[0].bank_id.bic if partner.bank_ids else ""
        return self.create_default_string_char(lng, default_value,
                                               value, fill, side)

    def get_number_benficiary_account(self, lng, default_value, fill, side):
        partner = self.line_body.partner_id
        value = partner.bank_ids[0].acc_number if partner.bank_ids else ""
        return self.create_default_string_char(lng, default_value,
                                               value, fill, side)

    def get_transaction_type(self, lng, default_value, fill, side):
        value = self.transaction_type
        if self.transaction_type == 'electronic_transaction':
            value = '37'
        else:
            value = self.transaction_type
        return self.create_default_string_char(lng, default_value,
                                               value, fill, side)

    def get_transaction_value(self, lng, default_value, fill, side):
        value = str(self.round_value(self.line_body.debit))
        return self.create_default_string_char(lng, default_value,
                                               value, fill, side)

    def get_reference(self, lng, default_value, fill, side):
        date = datetime.strptime(str(self.application_date), '%Y-%m-%d').month
        value = self.Month_homologation_2.get(calendar.month_abbr[date], '')
        value = "NOMINA   " + value
        return self.create_default_string_char(lng, default_value,
                                               value, fill, side)

        # main process
    def get_collect_data_bank(self):
        if self.bank_bic == '07':
            header = self.get_header_file_bancolombia()
            body = self.get_body_file_bancolombia()
            return header + body
        inherit_method = super().get_collect_data_bank()
        return inherit_method
