# -*- coding: utf-8 -*-

import csv
import math
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from ast import literal_eval

from odoo import models, fields, api, _
from odoo.modules.module import get_module_resource
import logging
_logger = logging.getLogger(__name__)


class AccountFlatFileParafiscal(models.TransientModel):
    _inherit = "account.flat.file.base"

    file_extension = fields.Selection(
        string='File Extension',
        selection_add=[('csv', 'CSV')]
    )

    employee_id = fields.Many2one('hr.employee', 'Employees')
    social_security_id = fields.Many2one("social.security", "Social Security")

    file_type = fields.Selection(
        selection_add=[('get_collect_data_parafiscal', 'Parafiscales')])

    template_modality = fields.Selection([
        ('0', 'None'),
        ('1', 'Electronic'),
        ('2', 'Assisted')
    ], string="Template Modality", default='1')

    template_type = fields.Selection([
        ('E', 'Employees'),
        ('Y', 'Independent Companies'),
        ('A', 'Contributors with Income News'),
        ('I', 'Independent'),
        ('S', 'Domestic Service Employees'),
        ('M', 'Blackberry'),
        ('N', 'Corrections'),
        ('H', 'Surrogate Mothers'),
        ('T', 'Employees Beneficiary Entity of the SG of Participations'),
        ('F', 'Payment of Missing Employer Contribution'),
        ('J', 'Social Security Payment in Compliance with the Judgment'),
        ('X', 'Payment of Liquidated Company'),
        ('U', 'UGPP for Third Party Payment'),
        ('K', 'Students')
    ], string="Template Type", default="E")

    period_1 = fields.Date(
        default=datetime.now().strftime('%Y-%m-01'))
    period_2 = fields.Date(
        default=str(datetime.now() + relativedelta(
            months=+2, day=1, days=-1))[:10])

    # campo associated template number falta campo para las opciones N, F, U
    associated_template_number = fields.Char(
        string="Associated Template Number", size=10, default=" ")

    payment_date_associated_template = fields.Char(
        string="Payment date of associated template", size=10, default=" ")

    def _get_identification_type(self, identification_type):
        dict_identificacion_type = {
            '31': 'NI', '13': 'CC',
            '22': 'CE', '41': 'PA'
        }
        return dict_identificacion_type.get(identification_type, '')

    def _character_quantity(self, value, maximum_character):
        total = maximum_character-len(value)
        return total

    def _get_header_file_parafiscal(self, totals):
        type_register = str(self.set_data_field(
            {'end': 1, 'start': 0, 'type': 'N', 'long': '2'}, str(1)))
        template_modality = str(self.template_modality)
        sequence = str(self.set_data_field(
            {'end': 6, 'start': 3, 'type': 'N', 'long': '4'}, str(1)))

        display_name = self.partner_id.display_name or ''

        company_id = self.env.ref('base.main_company')

        company_name = str(self.set_data_field(
            {'end': 206, 'start': 7, 'type': 'A', 'long': '200'},
            str(company_id.name)))

        # identification_type = self._get_identification_type(
        # self.partner_id.document_type)

        identification_type = 'NI'
        # num_id = company_id.vat or ''

        num_id = num_id = company_id.vat or ''
        num_id = num_id.split("-")[0] if \
            num_id.find("-") != -1 else num_id

        identification_number_taxpayer = (
            num_id
            + " "*self._character_quantity(
                num_id, 16))

        verification_digit_taxpayer = "0"
        associated_template_number = (
            self.associated_template_number
            + " "*self._character_quantity(
                self.associated_template_number, 10))

        payment_date_associated_template = (
            self.payment_date_associated_template
            + " "*self._character_quantity(
                self.payment_date_associated_template, 10))

        form_presentation = "U"

        taxpayer_branch_code = (
            " "*self._character_quantity(" ", 11))

        taxpayer_branch_name = (
            " "*self._character_quantity(" ", 41))

        _user = self.env['ir.config_parameter'].sudo()
        arl_id = _user.get_param('hr_payroll.entity_arl_id')
        arl = self.env['social.security'].browse(int(arl_id))
        code = arl.code if arl else ''
        arl_code = code + " " * self._character_quantity(code, 6)

        PILA_filing_number = (
            "0" + "0"*self._character_quantity(
                "0", 10))

        payment_date = (
            " " + " "*self._character_quantity(
                " ", 10))

        total = len(totals)
        total_employees = (
            "0"*self._character_quantity(
                str(total), 5)
            + str(total))
        total = int(sum([line for line in totals]))
        total_payroll_value = (
            "0"*self._character_quantity(
                str(total), 12) + str(total))
        contributor_type = "01"
        information_operator_code = "00"
        header = (
            type_register
            + template_modality
            + sequence
            + company_name.upper()
            + identification_type
            + identification_number_taxpayer
            + verification_digit_taxpayer
            + self.template_type
            + associated_template_number
            + payment_date_associated_template
            + form_presentation
            + taxpayer_branch_code
            + taxpayer_branch_name
            + arl_code
            + self.period_1.strftime('%Y-%m')
            + self.period_2.strftime('%Y-%m')
            + PILA_filing_number
            + payment_date
            + total_employees
            + total_payroll_value
            + contributor_type
            + information_operator_code + '\n')
        return bytes(header, 'utf8')

    def set_data_field(self, row, data):
        ele_type = row.get('type')
        ele_long = row.get('long')

        character = '0' if ele_type == 'N' else ' '
        left = True if ele_type == 'N' else False
        count = self._character_quantity(data, int(ele_long))
        res = (
            str(
                character)*count)+data if left else data+(str(character)*count)
        return res

    # Informacion Basica
    # SIMILAR PARA TODAS LA NOVEDADES QUE GENERAN LINEAS ADICIONALES

    # Obligatorio. Debe ser 02.
    # LISTO
    def compute_field_1(self, row, payslip, sequence, localdict):
        type_register = 2
        return str(self.set_data_field(row, str(type_register)))

    # Sequencia
    # Debe iniciar en 00001 y ser secuencial para el resto.
    # LISTO
    def compute_field_2(self, row, payslip, sequence, localdict):
        return str(self.set_data_field(row, str(sequence)))

    # Tipo documento del cotizante
    # CC CE TI PA CD SC RC
    # LISTO
    def compute_field_3(self, row, payslip, sequence, localdict):
        field_elem = self._get_identification_type(
            payslip.employee_id.document_type)
        return str(self.set_data_field(row, str(field_elem)))

    # Número de identificación del cotizante
    # LISTO
    def compute_field_4(self, row, payslip, sequence, localdict):
        field_elem = payslip.employee_id.identification_id or ''
        return str(self.set_data_field(row, str(field_elem)))

    # Tipo cotizante
    # LISTO
    def compute_field_5(self, row, payslip, sequence, localdict):
        field_elem = payslip.employee_id.contributor_type.code \
            if payslip.employee_id.contributor_type else 0
        return str(self.set_data_field(row, str(field_elem)))

    # Subtipo de cotizante
    # LISTO
    def compute_field_6(self, row, payslip, sequence, localdict):
        field_elem = payslip.employee_id.contributor_subtype.code \
            if payslip.employee_id.contributor_subtype else 0
        return str(self.set_data_field(row, str(field_elem)))

    # Extranjero no obligado a cotizar a pensiones
    # Puede ser blanco o X
    # LISTO
    def compute_field_7(self, row, payslip, sequence, localdict):
        field_elem = 'X' if payslip.contract_id\
            .pensions_contrib else ''
        return str(self.set_data_field(row, str(field_elem)))

    # Colombiano en el exterior
    # Puede ser blanco o X
    # LISTO
    def compute_field_8(self, row, payslip, sequence, localdict):
        field_elem = 'X' if payslip.contract_id.colombian_abroad else ''
        return str(self.set_data_field(row, str(field_elem)))

    # Código del departamento de la ubicación laboral
    # DIVIPOLA expedida por el DANE
    # LISTO
    def compute_field_9(self, row, payslip, sequence, localdict):
        field_elem = payslip.employee_id.address_home_id.divipola_state or ''
        return str(self.set_data_field(row, str(field_elem)))

    # Código del municipio de ubicación laboral
    # DIVIPOLA expedida por el DANE
    # LISTO
    def compute_field_10(self, row, payslip, sequence, localdict):
        field_elem = payslip.employee_id.address_home_id.divipola_town or ''
        ele_long = row.get('long')
        pos = int(ele_long)
        field_elem = field_elem[-pos:] \
            if len(field_elem) > int(ele_long) else field_elem
        return str(self.set_data_field(row, str(field_elem)))

    # TODO: Se recomienda tener, primer nombre, segundo nombre
    # Primer apellido segundo apellido
    # Julio Marco Alejandro Del Castillo Martínez

    # Primer Apellido
    # LISTO
    def compute_field_11(self, row, payslip, sequence, localdict):
        words = payslip.employee_id.surnames.split() \
            if payslip.employee_id.surnames else []
        field_elem = words[0] if len(words) > 0 and words[0] else ''
        field_elem = self.set_data_field(row, str(field_elem))
        return str(field_elem).upper().replace('Ñ', 'N')

    # Segundo Apellido
    # LISTO
    def compute_field_12(self, row, payslip, sequence, localdict):
        words = payslip.employee_id.surnames.split() \
            if payslip.employee_id.surnames else []
        field_elem = words[1] if len(words) > 1 and words[1] else ''
        field_elem = self.set_data_field(row, str(field_elem))
        return str(field_elem).upper().replace('Ñ', 'N')

    # Primer Nombre
    # LISTO
    def compute_field_13(self, row, payslip, sequence, localdict):
        words = payslip.employee_id.names.split() \
            if payslip.employee_id.names else []
        field_elem = words[0] if len(words) > 0 and words[0] else ''
        field_elem = self.set_data_field(row, str(field_elem))
        return str(field_elem).upper().replace('Ñ', 'N')

    # Segundo Nombre
    # LISTO
    def compute_field_14(self, row, payslip, sequence, localdict):
        words = payslip.employee_id.names.split() \
            if payslip.employee_id.names else []
        field_elem = words[1] if len(words) > 1 and words[1] else ''
        field_elem += words[2] if len(words) > 2 and ' ' + words[2] else ''
        field_elem = self.set_data_field(row, str(field_elem))
        return str(field_elem).upper().replace('Ñ', 'N')

    # FIN Informacion Basica

    # INICIO NOVEDADES

    def get_transfer(self, payslip, code, date_from=None, date_to=None):
        domain = [
            ('entity_type', '=', code),
            ('employee_id', '=', payslip.employee_id.id),
            ('state', '=', 'validate')]
        if date_from:
            domain += [('request_date', '>=', date_from)]
        if date_to:
            domain += [('request_date', '<=', date_to)]

        return self.env['social.security.transfer'].search(domain, limit=1)

    def get_for_transfer(self, payslip, code):
        return self.env['social.security.transfer'].search([
            ('entity_type', '=', code),
            ('employee_id', '=', payslip.employee_id.id),
            ('state', '=', 'draft'),
        ], limit=1)

    def get_config_rules(self, payslip, param="vst_rule_ids",
                         is_ids=False, line_ids=False):
        str_ids = self.env['ir.config_parameter'].sudo()\
            .get_param('many2many.' + param)

        if not str_ids:
            return False

        _ids = literal_eval(str_ids)
        if is_ids:
            return _ids
        lines = payslip.line_ids.filtered(
            lambda line: line.salary_rule_id.id in _ids)
        if line_ids:
            return lines.ids
        return len(lines) > 0 or False

    # ING: Ingreso
    # Puede ser un blanco, R, X o C
    # LISTO
    def compute_field_15(self, row, payslip, sequence, localdict):
        date_from = fields.Datetime.from_string(payslip.date_from).date()
        date_to = fields.Datetime.from_string(payslip.date_to).date()
        date_start = fields.Datetime.from_string(
            payslip.contract_id.date_start).date()
        field_elem = 'X' if date_from <= date_start <= date_to else ''
        localdict['ING'] = field_elem == 'X' or False
        return str(self.set_data_field(row, str(field_elem)))

    # RET: Retiro
    # Puede ser un blanco, P, R, X o C
    # Verificar con el modulo de liquidaciones
    # LISTO
    def compute_field_16(self, row, payslip, sequence, localdict):
        field_elem = ''

        settlement_id = self.env['settlement.history'].search([
            ('payslip_id', '=', payslip.id)
        ], limit=1)

        if settlement_id and settlement_id.date_payment:
            date_from = fields.Datetime.from_string(payslip.date_from).date()
            date_to = fields.Datetime.from_string(payslip.date_to).date()
            date_payment = fields.Datetime.from_string(
                settlement_id.date_payment).date()
            localdict['RET_DATE'] = date_payment
            field_elem = 'X' if date_from <= date_payment <= date_to else ''
        localdict['RET'] = field_elem == 'X' or False
        return str(self.set_data_field(row, str(field_elem)))

    # TDE: Traslado desde otra EPS o EOC
    # Puede ser blanco o X
    # LISTO
    def compute_field_17(self, row, payslip, sequence, localdict):
        transfer = self.get_transfer(payslip, 'health')
        field_elem = 'X' if transfer else ''
        localdict['TDE'] = transfer if transfer else False
        return str(self.set_data_field(row, str(field_elem)))

    # TAE: Traslado a otra EPS o EOC
    # Puede ser blanco o X
    # LISTO
    def compute_field_18(self, row, payslip, sequence, localdict):
        transfer = self.get_for_transfer(payslip, 'health')
        field_elem = 'X' if transfer else ''
        localdict['TDA'] = transfer if transfer else False
        return str(self.set_data_field(row, str(field_elem)))

    # TDP: Traslado desde otra administradora de pensiones
    # Puede ser blanco o X
    # LISTO
    def compute_field_19(self, row, payslip, sequence, localdict):
        transfer = self.get_transfer(payslip, 'pension')
        field_elem = 'X' if transfer else ''
        localdict['TDP'] = transfer if transfer else False
        return str(self.set_data_field(row, str(field_elem)))

    # TAP: Traslado a otra administradora de pensiones
    # Puede ser blanco o X
    # LISTO
    def compute_field_20(self, row, payslip, sequence, localdict):
        transfer = self.get_for_transfer(payslip, 'pension')
        field_elem = 'X' if transfer else ''
        localdict['TAP'] = transfer if transfer else False
        return str(self.set_data_field(row, str(field_elem)))

    def get_contract_variation(self, payslip, date_from=None, date_to=None):
        domain = [
            ('_type', '=', 'wage'),
            ('contract_id', '=', payslip.contract_id.id)]
        if date_from:
            domain += [('date', '>=', date_from)]
        if date_to:
            domain += [('date', '<=', date_to)]

        return self.env['hr.contract.history'].search(domain, limit=1)

    # VSP: Variacion permanente del salario
    # Puede ser blanco o X
    # Verificar aumento de sueldo con el historico de cambio de sueldo
    # MODULO hr_contract_history
    # LISTO
    def compute_field_21(self, row, payslip, sequence, localdict):
        transfer = self.get_contract_variation(
            payslip, payslip.date_from, payslip.date_to)
        field_elem = 'X' if transfer else ''
        localdict['VSP'] = transfer if transfer else False
        localdict['VSP_DATE'] = transfer.date if transfer else False
        return str(self.set_data_field(row, str(field_elem)))

    # Correcciones
    # Puede ser blanco, A o C
    # LISTO
    def compute_field_22(self, row, payslip, sequence, localdict):
        field_elem = ''
        return str(self.set_data_field(row, str(field_elem)))

    # VST: Variacion transitoria del salario
    # Puede ser blanco o X
    # LISTO
    def compute_field_23(self, row, payslip, sequence, localdict):
        retiro = localdict.get('RET', False)
        field_elem = 'X' if self.get_config_rules(payslip) or retiro else ''
        return str(self.set_data_field(row, str(field_elem)))

    # SLN: Suspencion temporal del contrato laboral o
    # licencia no remunerada o comision de servicios
    # Puede ser Blanco, X o C
    # Genera linea adicional en el archivo plano
    # LISTO
    def compute_field_24(self, row, payslip, sequence, localdict):
        line_ids = self.get_config_rules(
            payslip, 'sln_rule_ids', line_ids=True)
        field_elem = ''
        localdict.update(SLN={
            'ids': line_ids,
        } if line_ids and len(line_ids) > 0 else False)
        return str(self.set_data_field(row, str(field_elem)))

    # IGE: Incapacidad temporal por enfermedad general
    # Puede ser Blanco o X
    # Genera linea adicional en el archivo plano
    # LISTO
    def compute_field_25(self, row, payslip, sequence, localdict):
        line_ids = self.get_config_rules(
            payslip, 'ige_rule_ids', line_ids=True)
        field_elem = ''
        localdict.update(IGE={
            'ids': line_ids,
        } if line_ids and len(line_ids) > 0 else False)
        return str(self.set_data_field(row, str(field_elem)))

    # LMA: Licencia de maternidad o de Paternidad
    # Puede ser Blanco o X
    # Genera linea adicional en el archivo plano
    # LISTO
    def compute_field_26(self, row, payslip, sequence, localdict):
        line_ids = self.get_config_rules(
            payslip, 'lma_rule_ids', line_ids=True)
        field_elem = ''
        localdict.update(LMA={
            'ids': line_ids,
        } if line_ids and len(line_ids) > 0 else False)
        return str(self.set_data_field(row, str(field_elem)))

    # VAC - LR: Vacaciones, Licencia remunerada
    # Puede ser X, L o Blanco (PENDINTE)
    # Genera linea adicional en el archivo plano
    # LISTO
    def compute_field_27(self, row, payslip, sequence, localdict):
        line_ids = self.get_config_rules(
            payslip, 'vac_lr_rule_ids', line_ids=True)
        field_elem = ''
        localdict.update(VAC_LR={
            'ids': line_ids,
        } if line_ids and len(line_ids) > 0 else False)
        return str(self.set_data_field(row, str(field_elem)))

    # AVP: Aporte Voluntario
    # Puede ser Blanco o X
    # LISTO
    def compute_field_28(self, row, payslip, sequence, localdict):
        field_elem = 'X'\
            if self.get_config_rules(payslip, 'avp_rule_ids') else ''
        return str(self.set_data_field(row, str(field_elem)))

    # VCT: Variacion centros de trabajo
    # Puede ser Blanco o X
    # LISTO
    def compute_field_29(self, row, payslip, sequence, localdict):
        transfer = self.get_transfer(
            payslip, 'risk_class', payslip.date_from, payslip.date_to)
        field_elem = 'X' if transfer else ''
        localdict['VCT'] = transfer if transfer else False
        return str(self.set_data_field(row, str(field_elem)))

    # IRL: Dias de incapacidad por accidente de trabajo
    # o enfermedad laboral
    # Puede ser (0) o el numero de dias entre (1 y 30)
    # Genera linea adicional en el archivo plano
    # LISTO
    def compute_field_30(self, row, payslip, sequence, localdict):
        line_ids = self.get_config_rules(
            payslip, 'irl_rule_ids', line_ids=True)
        field_elem = ''
        localdict.update(IRL={
            'ids': line_ids,
        } if line_ids and len(line_ids) > 0 else False)
        return str(self.set_data_field(row, str(field_elem)))

    # FIN NOVEDADES localdict

    # Codigo de la administradora del fondo de pensiones
    # a la cual pertenece el afiliado
    # SS feature-3564
    # LISTO
    def compute_field_31(self, row, payslip, sequence, localdict):
        field_elem = payslip.employee_id.pension.code \
            if payslip.employee_id.pension else ''
        return str(self.set_data_field(row, str(field_elem)))

    # Codigo de la administradora de fondo de pensiones
    # a la cual se traslada el afiliado
    # Solo si el campo 19 fue completado con una X
    # Solo si la novedad es traslado a  otra administradora
    # de fondo de pensiones
    # LISTO
    def compute_field_32(self, row, payslip, sequence, localdict):
        transfer = localdict.get('TAP', False)
        field_elem = transfer.social_security_new.code \
            if transfer and transfer.social_security_new else ''
        return str(self.set_data_field(row, str(field_elem)))

    # Codigo de EPS o EOC a la cual pertenece el afiliado
    # LISTO
    def compute_field_33(self, row, payslip, sequence, localdict):
        field_elem = payslip.employee_id.health.code \
            if payslip.employee_id.health else ''
        return str(self.set_data_field(row, str(field_elem)))

    # Codigo de EPS o EOC a la cual se traslada el afiliado
    # Solo si el campo 18 fue completado con una X
    # SS feature-3564
    # LISTO
    def compute_field_34(self, row, payslip, sequence, localdict):
        transfer = localdict.get('TDA', False)
        field_elem = transfer.social_security_new.code \
            if transfer and transfer.social_security_new else ''
        return str(self.set_data_field(row, str(field_elem)))

    # Codigo CCF a la cual pertenece el afiliado
    # Solo se permite blanco si el tipo de cotizante
    # no esta obligado a aportar a CCF
    # SS feature-3564
    # LISTO
    def compute_field_35(self, row, payslip, sequence, localdict):
        field_elem = payslip.employee_id.compensation_box.code \
            if payslip.employee_id.compensation_box else ''
        return str(self.set_data_field(row, str(field_elem)))

    # Numeros de Dias cotizados a pension
    # Valores entre (0 y 30), si es menor a 30
    # debe haber una novedad de ingreso o retiro
    # Validar por el codigo de la regla
    # LISTO
    def compute_field_36(self, row, payslip, sequence, localdict, days=0):
        field_elem = int(days)
        if days == 0:
            lines = payslip.line_ids.filtered(
                lambda line: line.code == 'BASIC')
            field_elem = int(sum([line.quantity for line in lines]))
        field_elem = 0 if not payslip.employee_id.pension else field_elem
        return str(self.set_data_field(row, str(field_elem)))

    # Numeros de dias cotizados a salud
    # Valores entre (0 y 30), si es menor a 30
    # debe haber una novedad de ingreso o retiro
    # LISTO
    def compute_field_37(self, row, payslip, sequence, localdict, days=0):
        field_elem = int(days)
        if days == 0:
            lines = payslip.line_ids.filtered(
                lambda line: line.code == 'BASIC')
            field_elem = int(sum([line.quantity for line in lines]))
        return str(self.set_data_field(row, str(field_elem)))

    # Numeros de dias cotizados a riesgos laborales
    # Valores entre (0 y 30)
    # 0 si el cotizante no esta obligado a aportar al
    # sistema general de riesgos laborales o si los campos
    # 25,26,27 se marcaron con X o si el campo 30 es mayor a 0
    # si es menor que 30 debe haber marcado la novedad correspondiente
    # LISTO
    def compute_field_38(self, row, payslip, sequence, localdict, days=0):
        field_elem = int(days)
        if days == 0:
            lines = payslip.line_ids.filtered(
                lambda line: line.code == 'BASIC')
            field_elem = int(sum([line.quantity for line in lines]))
        field_elem = 0 if not payslip.employee_id.arl else field_elem
        return str(self.set_data_field(row, str(field_elem)))

    # Numero de dias cotizados a la caja de compensacion familiar
    # Valores entre (0 y 30), solo 0 si el tipo de cotizante no esta
    # obligado a aportar a la caja de compenzacion familiar, si es
    # menor a 30 debe haber marcado la novedad correspondiente
    # LISTO
    def compute_field_39(self, row, payslip, sequence, localdict, days=0):
        field_elem = int(days)
        if days == 0:
            lines = payslip.line_ids.filtered(
                lambda line: line.code == 'BASIC')
            field_elem = int(sum([line.quantity for line in lines]))
        field_elem = 0 if not payslip.employee_id.compensation_box\
            else field_elem
        return str(self.set_data_field(row, str(field_elem)))

    # Salario basico
    # sin comas ni puntos, no puede ser menor a 0
    # puede ser menor a 1 smlv
    # Minímo el SMLV
    # sin centavos
    # LISTO
    def compute_field_40(self, row, payslip, sequence, localdict):
        field_elem = int(payslip._get_paid_amount())
        _ids = self.get_config_rules(
            payslip, 'sena_salary_structure_ids', True)
        field_elem = int(payslip.company_id.basic_salary)\
            if _ids and payslip.struct_id.id in _ids else field_elem
        field_elem = self.basic_salary_validator(field_elem, payslip)
        return str(self.set_data_field(row, str(field_elem)))

    # Validador salario básico
    # Si el salario básico no puede ser menor al SMLV
    def basic_salary_validator(self, basic_salary, payslip):
        min_wage = int(payslip.company_id.basic_salary)
        basic_salary = min_wage if basic_salary < min_wage else basic_salary
        return basic_salary

    # Salario integral
    # Puede ser Blanco o X
    # NOTA: F para salario fijo
    # Para los senas debe ir vacio
    # LISTO
    def compute_field_41(self, row, payslip, sequence, localdict):
        _ids = self.get_config_rules(
            payslip, 'integral_salary_structure_ids', True)
        field_elem = 'X' \
            if _ids and payslip.struct_id.id in _ids else ' '
        localdict['is_integral'] = bool(field_elem == 'X')
        _ids = self.get_config_rules(
            payslip, 'sena_salary_structure_ids', True)
        field_elem = '' if _ids and payslip.struct_id.id in _ids\
            else field_elem
        return str(self.set_data_field(row, str(field_elem)))

    # INICIO IBC

    # IBC pension
    # LISTO
    def compute_field_42(self, row, payslip, sequence, localdict, total=0):
        field_elem = total
        if total == 0:
            lines = payslip.line_ids.filtered(lambda line: line.code == '3020')
            field_elem = math.ceil(sum([line.amount for line in lines]))
        localdict['field_42'] = field_elem
        return str(self.set_data_field(row, str(field_elem)))

    # IBC salud
    # LISTO
    def compute_field_43(self, row, payslip, sequence, localdict, total=0):
        field_elem = total
        _ids = self.get_config_rules(
            payslip, 'sena_salary_structure_ids', True)
        codes = ['3010']
        if _ids and payslip.struct_id.id in _ids:
            codes += ['SALU']
        if total == 0:
            lines = payslip.line_ids.filtered(lambda line: line.code in codes)
            field_elem = math.ceil(sum([line.amount for line in lines]))
        localdict['field_43'] = field_elem
        return str(self.set_data_field(row, str(field_elem)))

    # IBC riesgos laborales
    # LISTO
    def compute_field_44(self, row, payslip, sequence, localdict, total=0):
        field_elem = total
        if total == 0:
            lines = payslip.line_ids.filtered(lambda line: line.code == 'ARL')
            field_elem = math.ceil(sum([line.amount for line in lines]))
        localdict['field_44'] = field_elem
        return str(self.set_data_field(row, str(field_elem)))

    # IBC CCF
    # Validar con novedades lineas extras
    # LISTO
    def compute_field_45(self, row, payslip, sequence, localdict, total=0):
        codes = ['CAJA']
        if localdict.get('RET', False):
            codes += ['150']

        field_elem = total
        if total == 0:
            lines = payslip.line_ids.filtered(lambda line: line.code in codes)
            field_elem = int(sum([line.amount for line in lines]))
        localdict['field_45'] = field_elem
        return str(self.set_data_field(row, str(field_elem)))

    # FIN IBC

    # Tarifa de aportes pensiones
    # LISTO
    def compute_field_46(self, row, payslip, sequence,
                         localdict, codes=['3020', 'PENS']):
        lines = payslip.line_ids.filtered(lambda line: line.code in codes)
        field_elem = sum([abs(line.rate) for line in lines])/100 \
            if len(lines) > 0 else 0
        localdict['field_46'] = field_elem
        return str(self.set_data_field(row, str(field_elem)))

    # Cotizacion obligaria al fondo de pensiones
    # LISTO
    def compute_field_47(self, row, payslip, sequence, localdict):
        field_elem = int(localdict.get('field_42', 0) *
                         localdict.get('field_46', 0))
        localdict['field_47'] = int(field_elem)
        return str(self.set_data_field(row, str(field_elem)))

    # Aporte voluntario del afiliado al fondo de pensiones
    # obligatoria
    # LISTO
    def compute_field_48(self, row, payslip, sequence, localdict):
        _ids = self.get_config_rules(payslip, 'avp_rule_ids', line_ids=True)
        lines = self.env['hr.payslip.line'].browse(_ids)
        field_elem = int(sum([abs(line.total) for line in lines]))
        localdict['field_48'] = field_elem
        return str(self.set_data_field(row, str(field_elem)))

    # Aporte voluntario del aportante al fondo de pensiones
    # obligatoria
    # CREAR NOVEDAD PARA EL EMPLEADOR
    # LISTO
    def compute_field_49(self, row, payslip, sequence, localdict):
        field_elem = int(0)
        localdict['field_49'] = field_elem
        return str(self.set_data_field(row, str(field_elem)))

    # Total cotizacion Sistema general de fondo de pensiones
    # Calculado por el sistema suma de los campos 47, 48 y 49
    # LISTO
    def compute_field_50(self, row, payslip, sequence, localdict):
        field_47 = localdict.get('field_47', 0)
        field_48 = localdict.get('field_48', 0)
        field_49 = localdict.get('field_49', 0)
        field_elem = int(float(field_47) + float(field_48) + float(field_49))
        return str(self.set_data_field(row, str(field_elem)))

    # Aportes a fondo de solidaridad pensional - subcuenta
    # de solidaridad
    # Crear campo para expecificar que porcentaje debe llevar 3020
    # LISTO
    def compute_field_51(self, row, payslip, sequence, localdict):
        _user = self.env['ir.config_parameter'].sudo()
        rate = float(_user.get_param('hr_payroll.rate_subsistence_afs'))
        lines = payslip.line_ids.filtered(lambda line: line.code == '3023')
        ibc = sum([abs(line.total) for line in lines])
        ibc2 = sum([abs(line.amount) for line in lines])
        field_elem = int(ibc*(rate/100))
        localdict['field_51'] = field_elem
        localdict['field_51_ibc'] = ibc
        return str(self.set_data_field(row, str(field_elem)))

    # Aportes a fondo de solidariada pensional-subcuenta subsistencia
    # Crear campo para expecificar que porcentaje debe llevar 3020
    # LISTO
    def compute_field_52(self, row, payslip, sequence, localdict):
        _user = self.env['ir.config_parameter'].sudo()
        rate = float(_user.get_param('hr_payroll.rate_solidarity_afs'))
        lines = payslip.line_ids.filtered(lambda line: line.code == '3023')
        ibc = sum([abs(line.total) for line in lines])
        ibc2 = sum([abs(line.amount) for line in lines])
        field_elem = int(ibc*(rate/100))
        localdict['field_52'] = field_elem
        localdict['field_52_ibc'] = ibc
        return str(self.set_data_field(row, str(field_elem)))

    # Valor no retenido por aportes voluntarios
    # NUEVO RQ
    # PENDIENTE
    def compute_field_53(self, row, payslip, sequence, localdict):
        field_elem = 0
        return str(self.set_data_field(row, str(field_elem)))

    # Tarifa de aportes salud
    # LISTO
    def compute_field_54(self, row, payslip, sequence,
                         localdict, codes=['3010', 'SALU']):
        lines = payslip.line_ids.filtered(lambda line: line.code in codes)
        field_elem = sum([abs(line.rate) for line in lines])/100 \
            if len(lines) > 0 else 0
        localdict['field_55'] = sum([abs(line.total) for line in lines])
        localdict['field_54'] = field_elem
        return str(self.set_data_field(row, str(field_elem)))

    # Cotizacion obligatoria a salud
    # LISTO
    def compute_field_55(self, row, payslip, sequence, localdict):
        lines = payslip.line_ids.filtered(lambda line: line.code == '3010')
        field_elem = int(sum([abs(line.total) for line in lines]))
        _ids = self.get_config_rules(
            payslip, 'sena_salary_structure_ids', True)
        field_elem = int(localdict.get(
                            'field_43', 0) * localdict.get(
                                'field_54', 0))\
            if _ids and payslip.struct_id.id in _ids and\
            localdict.get('field_55_calculate', False)\
            else field_elem
        localdict['field_55'] = int(field_elem)
        return str(self.set_data_field(row, str(field_elem)))

    # Valor de la UPC adicional
    # tipo de cotizante 40-Beneficiario de UPC Adicional
    # NUEVO RQ
    # PENDIENTE
    def compute_field_56(self, row, payslip, sequence, localdict):
        field_elem = 0
        return str(self.set_data_field(row, str(field_elem)))

    # Numero autorización de la incapacidad por enfermedad general
    # Debe reportarse en blanco.
    # LISTO
    def compute_field_57(self, row, payslip, sequence, localdict):
        field_elem = ''
        return str(self.set_data_field(row, str(field_elem)))

    # Valor de la incapacidad por enfermedad general
    # Debe reportarse en 0
    # LISTO
    def compute_field_58(self, row, payslip, sequence, localdict):
        field_elem = 0
        return str(self.set_data_field(row, str(field_elem)))

    # N° de autorización de la licencia de
    # maternidad o paternidad
    # Debe reportarse en blanco
    # LISTO
    def compute_field_59(self, row, payslip, sequence, localdict):
        field_elem = ''
        return str(self.set_data_field(row, str(field_elem)))

    # Valor de la licencia de maternidad
    # Debe reportarse en cero
    # LISTO
    def compute_field_60(self, row, payslip, sequence, localdict):
        field_elem = 0
        return str(self.set_data_field(row, str(field_elem)))

    # Tarifa de aportes a Riesgos Laborales
    # LISTO
    def compute_field_61(self, row, payslip, sequence,
                         localdict, codes=['ARL']):
        lines = payslip.line_ids.filtered(lambda line: line.code in codes)
        field_elem = sum([abs(line.rate) for line in lines])/100
        localdict['field_61'] = field_elem
        return str(self.set_data_field(row, str(field_elem)))

    # Centro de Trabajo CT
    # Debe existir cuando exista código de ARL. Debe ser
    # suministrado por el aportante con
    # base en los códigos de centros de trabajo definidos por la ARL
    # NUEVO
    # PENDIENTE
    def compute_field_62(self, row, payslip, sequence, localdict):
        field_elem = 0
        return str(self.set_data_field(row, str(field_elem)))

    # Cotización obligatoria al Sistema
    # General de Riesgos Laborales
    # LISTO
    def compute_field_63(self, row, payslip, sequence, localdict):
        lines = payslip.line_ids.filtered(lambda line: line.code == 'ARL')
        field_elem = int(sum([abs(line.total) for line in lines]))
        field_elem = int(localdict.get(
                            'field_44', 0) * localdict.get('field_61', 0))\
            if localdict.get('field_63_calculate', False) else field_elem
        localdict['field_63'] = int(field_elem)
        return str(self.set_data_field(row, str(field_elem)))

    # Tarifa de aportes CCF
    # LISTO
    def compute_field_64(self, row, payslip, sequence, localdict):
        lines = payslip.line_ids.filtered(lambda line: line.code == 'CAJA')
        field_elem = sum([abs(line.rate) for line in lines])/100
        localdict['field_64'] = field_elem
        return str(self.set_data_field(row, str(field_elem)))

    # Valor aporte CCF
    # LISTO
    def compute_field_65(self, row, payslip, sequence, localdict):
        # lines = payslip.line_ids.filtered(lambda line: line.code == 'CAJA')
        # field_elem = int(sum([abs(line.total) for line in lines]))
        field_elem = int(localdict.get('field_45', 0) *
                         localdict.get('field_64', 0))
        localdict['field_65'] = int(field_elem)
        return str(self.set_data_field(row, str(field_elem)))

    # Tarifa de aportes SENA
    # LISTO
    def compute_field_66(self, row, payslip, sequence, localdict):
        lines = payslip.line_ids.filtered(lambda line: line.code == 'SENA')
        field_elem = sum([abs(line.rate) for line in lines])/100
        localdict['field_66'] = field_elem
        return str(self.set_data_field(row, str(field_elem)))

    # Valor aportes SENA
    # LISTO
    def compute_field_67(self, row, payslip, sequence, localdict):
        lines = payslip.line_ids.filtered(lambda line: line.code == 'SENA')
        field_elem = int(sum([abs(line.total) for line in lines]))
        return str(self.set_data_field(row, str(field_elem)))

    # Tarifa aportes ICBF
    # LISTO
    def compute_field_68(self, row, payslip, sequence, localdict):
        lines = payslip.line_ids.filtered(lambda line: line.code == 'ICBF')
        field_elem = sum([abs(line.rate) for line in lines])/100
        localdict['field_68'] = field_elem
        return str(self.set_data_field(row, str(field_elem)))

    # Valor aporte ICBF
    # LISTO
    def compute_field_69(self, row, payslip, sequence, localdict):
        lines = payslip.line_ids.filtered(lambda line: line.code == 'ICBF')
        field_elem = int(sum([abs(line.total) for line in lines]))
        return str(self.set_data_field(row, str(field_elem)))

    # Tarifa aportes ESAP
    # LISTO
    def compute_field_70(self, row, payslip, sequence, localdict):
        lines = payslip.line_ids.filtered(lambda line: line.code == 'ESAP')
        field_elem = sum([abs(line.rate) for line in lines])/100
        return str(self.set_data_field(row, str(field_elem)))

    # Valor aporte ESAP
    # LISTO
    def compute_field_71(self, row, payslip, sequence, localdict):
        lines = payslip.line_ids.filtered(lambda line: line.code == 'ESAP')
        field_elem = sum([abs(line.total) for line in lines])
        return str(self.set_data_field(row, str(field_elem)))

    # Tarifa aportes MEN
    # LISTO
    def compute_field_72(self, row, payslip, sequence, localdict):
        lines = payslip.line_ids.filtered(lambda line: line.code == 'MEN')
        field_elem = sum([abs(line.rate) for line in lines])/100
        return str(self.set_data_field(row, str(field_elem)))

    # Valor aporte MEN
    # LISTO
    def compute_field_73(self, row, payslip, sequence, localdict):
        lines = payslip.line_ids.filtered(lambda line: line.code == 'MEN')
        field_elem = sum([abs(line.total) for line in lines])
        return str(self.set_data_field(row, str(field_elem)))

    # Tipo de documento del cotizante principal
    # Puede ser CC, CE, TI, PA, CD, SC
    # UPC adicional
    # PENDIENTE NUEVO
    def compute_field_74(self, row, payslip, sequence, localdict):
        field_elem = ''
        return str(self.set_data_field(row, str(field_elem)))

    # Número de identificación del cotizante principal
    # UPC adicional
    # PENDIENTE NUEVO
    def compute_field_75(self, row, payslip, sequence, localdict):
        field_elem = ''
        return str(self.set_data_field(row, str(field_elem)))

    # Cotizante exonerado de pago de aporte
    # salud, SENA e ICBF - Ley 1607 de 2012
    # Puede ser S o N, si valor del campo 43 es superior a
    # 10 SMLMV este campo debe ser N
    # LISTO
    def compute_field_76(self, row, payslip, sequence, localdict):
        _ids = self.get_config_rules(
            payslip, 'integral_salary_structure_ids', True)
        _ids += self.get_config_rules(
            payslip, 'sena_salary_structure_ids', True)
        field_elem = 'N' \
            if _ids and payslip.struct_id.id in _ids else 'S'
        return str(self.set_data_field(row, str(field_elem)))

    # Código de la administradora de Riesgos Laborales a
    # la cual pertenece el afiliado
    # LISTO
    def compute_field_77(self, row, payslip, sequence, localdict):
        field_elem = payslip.employee_id.arl.code or ''
        return str(self.set_data_field(row, str(field_elem)))

    # Clase de riesgo en la que se encuentra el afiliado
    # Informacion desde el contrato/empleado
    # Crear entidad para clase de riesgo
    # field_elem = payslip.contract_id.risk_class or ''
    # LISTO
    # CUANDO ES NOVEDAD SE DEJA VACIO
    def compute_field_78(self, row, payslip, sequence, localdict):
        field_elem = payslip.contract_id.risk_class.code or ''
        return str(self.set_data_field(row, str(field_elem)))

    # Indicador tarifa especial pensiones
    # Posibles valores: Blanco tarifa normal
    # 1. Actividades de alto riesgo
    # 2. Senadores
    # 3. CTI
    # 4. Aviadores
    # LISTO
    def compute_field_79(self, row, payslip, sequence, localdict):
        field_elem = payslip.contract_id.pension_special_rate_indicator or ''
        return str(self.set_data_field(row, str(field_elem)))

    # Fechas Novedades

    def _get_date_fields(self, row, date):
        field_elem = fields.Datetime.from_string(date).strftime('%Y-%m-%d')
        return str(self.set_data_field(row, str(field_elem)))

    # Fecha de ingreso Formato (AAAA-MM-DD).
    # LISTO
    def compute_field_80(self, row, payslip, sequence, localdict):
        field_elem = ''
        if localdict.get('ING', False):
            field_elem = fields.Datetime.from_string(
                payslip.contract_id.date_start).strftime('%Y-%m-%d')
        return str(self.set_data_field(row, str(field_elem)))

    # Fecha de retiro Formato (AAAA-MM-DD).
    # LISTO
    def compute_field_81(self, row, payslip, sequence, localdict):
        field_elem = ''
        if localdict.get('RET', False):
            date_end = localdict.get('RET_DATE')
            field_elem = fields.Datetime.from_string(
                date_end).strftime('%Y-%m-%d')
        return str(self.set_data_field(row, str(field_elem)))

    # Fecha Inicio VSP Formato (AAAA-MM-DD).
    # LISTO
    def compute_field_82(self, row, payslip, sequence, localdict):
        field_elem = ''
        if localdict.get('VSP', False):
            date_end = localdict.get('VSP_DATE')
            field_elem = fields.Datetime.from_string(
                date_end).strftime('%Y-%m-%d')
        return str(self.set_data_field(row, str(field_elem)))

    # Fecha Inicio SLN Formato (AAAA-MM-DD).
    # Se agrega en la novedad
    # LISTO
    def compute_field_83(self, row, payslip, sequence, localdict):
        field_elem = ''
        return str(self.set_data_field(row, str(field_elem)))

    # Fecha fin SLN Formato (AAAA-MM-DD).
    # Se agrega en la novedad
    # LISTO
    def compute_field_84(self, row, payslip, sequence, localdict):
        field_elem = ''
        return str(self.set_data_field(row, str(field_elem)))

    # Fecha inicio IGE Formato (AAAA-MM-DD).
    # Se agrega en la novedad
    # LISTO
    def compute_field_85(self, row, payslip, sequence, localdict):
        field_elem = ''
        return str(self.set_data_field(row, str(field_elem)))

    # Fecha fin IGE. formato (AAAA-MM-DD)
    # Se agrega en la novedad
    # LISTO
    def compute_field_86(self, row, payslip, sequence, localdict):
        field_elem = ''
        return str(self.set_data_field(row, str(field_elem)))

    # Fecha inicio LMA Formato (AAAA-MM-DD).
    # Se agrega en la novedad
    # LISTO
    def compute_field_87(self, row, payslip, sequence, localdict):
        field_elem = ''
        return str(self.set_data_field(row, str(field_elem)))

    # Fecha fin LMA formato (AAAA-MM-DD)
    # Se agrega en la novedad
    # LISTO
    def compute_field_88(self, row, payslip, sequence, localdict):
        field_elem = ''
        return str(self.set_data_field(row, str(field_elem)))

    # Fecha inicio VAC - LR Formato (AAAA-MM-DD).
    # Se agrega en la novedad
    # LISTO
    def compute_field_89(self, row, payslip, sequence, localdict):
        field_elem = ''
        return str(self.set_data_field(row, str(field_elem)))

    # Fecha fin VAC - LR Formato (AAAA-MM-DD).
    # Se agrega en la novedad
    # LISTO
    def compute_field_90(self, row, payslip, sequence, localdict):
        field_elem = ''
        return str(self.set_data_field(row, str(field_elem)))

    # Fecha inicio VCT Formato (AAAA-MM-DD).
    # LISTO
    def compute_field_91(self, row, payslip, sequence, localdict):
        field_elem = ''
        if localdict.get('VCT', False):
            transfer = localdict.get('VCT')
            field_elem = transfer.date_start
        return str(self.set_data_field(row, str(field_elem)))

    # Fecha fin VCT Formato (AAAA-MM-DD).
    # LISTO
    def compute_field_92(self, row, payslip, sequence, localdict):
        field_elem = ''
        if localdict.get('VCT', False):
            transfer = localdict.get('VCT')
            field_elem = transfer.date_end
        return str(self.set_data_field(row, str(field_elem)))

    # Fecha inicio IRL Formato (AAAA-MM-DD).
    # Se agrega en la novedad
    # LISTO
    def compute_field_93(self, row, payslip, sequence, localdict):
        field_elem = ''
        return str(self.set_data_field(row, str(field_elem)))

    # Fecha fin IRL Formato (AAAA-MM-DD).
    # Se agrega en la novedad
    # LISTO
    def compute_field_94(self, row, payslip, sequence, localdict):
        field_elem = ''
        return str(self.set_data_field(row, str(field_elem)))

    # FIN Fechas Novedades

    # IBC otros parafiscales diferentes a CCF
    # SENA or ICBF
    # Obligatorio para los tipos de cotizante
    # 1, 18, 20, 22, 30, 31, 55
    def compute_field_95(self, row, payslip, sequence, localdict, total=0):
        field_elem = total
        if total == 0:
            lines = payslip.line_ids.filtered(lambda line: line.code == 'SENA')
            field_elem = int(sum([line.amount for line in lines]))
        return str(self.set_data_field(row, str(field_elem)))

    # Número de horas laboradas
    # Obligatorio para los tipos de cotizante
    # 1, 18, 20, 22, 30, 51, 55
    # LISTO
    def compute_field_96(self, row, payslip, sequence, localdict):
        field_elem = 240
        return str(self.set_data_field(row, str(field_elem)))

    def _get_data_fields(self):
        return [
            {'field': '1', 'end': 1, 'start': 0,
                'label': 'Tipo de registro',
                'type': 'N', 'long': '2'},
            {'field': '2', 'end': 6, 'start': 2,
                'label': 'Secuencia',
                'type': 'N', 'long': '5'},
            {'field': '3', 'end': 8, 'start': 7,
                'label': 'Tipo documento',
                'type': 'A', 'long': '2'},
            {'field': '4', 'end': 24, 'start': 9,
                'label': 'N documento',
                'type': 'A', 'long': '16'},
            {'field': '5', 'end': 26, 'start': 25,
                'label': 'Tipo cotizante',
                'type': 'N', 'long': '2'},
            {'field': '6', 'end': 28, 'start': 27,
                'label': 'Subtipo de cotizante',
                'type': 'N', 'long': '2'},
            {'field': '7', 'end': 29, 'start': 29,
                'label': 'Extranjero no obligado a cotizar a pensiones',
                'type': 'A', 'long': '1'},
            {'field': '8', 'end': 30, 'start': 30,
                'label': 'Colombiano en el exterior',
                'type': 'A', 'long': '1'},
            {'field': '9', 'end': 32, 'start': 31,
                'label': 'Código del departamento de la ubicación laboral',
                'type': 'A', 'long': '2'},
            {'field': '10', 'end': 35, 'start': 33,
                'label': 'Código del municipio de ubicación laboral',
                'type': 'A', 'long': '3'},
            {'field': '11', 'end': 55, 'start': 36,
                'label': 'Primer apellido',
                'type': 'A', 'long': '20'},
            {'field': '12', 'end': 85, 'start': 56,
                'label': 'Segundo apellido',
                'type': 'A', 'long': '30'},
            {'field': '13', 'end': 105, 'start': 86,
                'label': 'Primer nombre',
                'type': 'A', 'long': '20'},
            {'field': '14', 'end': 135, 'start': 106,
                'label': 'Segundo nombre',
                'type': 'A', 'long': '30'},
            {'field': '15', 'end': 136, 'start': 136,
                'label': 'ING',
                'type': 'A', 'long': '1'},
            {'field': '16', 'end': 137, 'start': 137,
                'label': 'RET',
                'type': 'A', 'long': '1'},
            {'field': '17', 'end': 138, 'start': 138,
                'label': 'TDE',
                'type': 'A', 'long': '1'},
            {'field': '18', 'end': 139, 'start': 139,
                'label': 'TAE',
                'type': 'A', 'long': '1'},
            {'field': '19', 'end': 140, 'start': 140,
                'label': 'TDP',
                'type': 'A', 'long': '1'},
            {'field': '20', 'end': 141, 'start': 141,
                'label': 'TAP',
                'type': 'A', 'long': '1'},
            {'field': '21', 'end': 142, 'start': 142,
                'label': 'VSP',
                'type': 'A', 'long': '1'},
            {'field': '22', 'end': 143, 'start': 143,
                'label': 'Correcciones',
                'type': 'A', 'long': '1'},
            {'field': '23', 'end': 144, 'start': 144,
                'label': 'VST',
                'type': 'A', 'long': '1'},
            {'field': '24', 'end': 145, 'start': 145,
                'label': 'SLN',
                'type': 'A', 'long': '1'},
            {'field': '25', 'end': 146, 'start': 146,
                'label': 'IGE',
                'type': 'A', 'long': '1'},
            {'field': '26', 'end': 147, 'start': 147,
                'label': 'LMA',
                'type': 'A', 'long': '1'},
            {'field': '27', 'end': 148, 'start': 148,
                'label': 'VAC - LR',
                'type': 'A', 'long': '1'},
            {'field': '28', 'end': 149, 'start': 149,
                'label': 'AVP',
                'type': 'A', 'long': '1'},
            {'field': '29', 'end': 150, 'start': 150,
                'label': 'VCT',
                'type': 'A', 'long': '1'},
            {'field': '30', 'end': 152, 'start': 151,
                'label': 'IRL',
                'type': 'N', 'long': '2'},
            {'field': '31', 'end': 158, 'start': 153,
                'label': 'Código Pension',
                'type': 'A', 'long': '6'},
            {'field': '32', 'end': 164, 'start': 159,
                'label': 'Código Pension traslado',
                'type': 'A', 'long': '6'},
            {'field': '33', 'end': 170, 'start': 165,
                'label': 'Código EPS o EOC',
                'type': 'A', 'long': '6'},
            {'field': '34', 'end': 176, 'start': 171,
                'label': 'Código EPS o EOC traslado',
                'type': 'A', 'long': '6'},
            {'field': '35', 'end': 182, 'start': 177,
                'label': 'Código CCF',
                'type': 'A', 'long': '6'},
            {'field': '36', 'end': 184, 'start': 183,
                'label': 'días pensión',
                'type': 'N', 'long': '2'},
            {'field': '37', 'end': 186, 'start': 185,
                'label': 'días salud',
                'type': 'N', 'long': '2'},
            {'field': '38', 'end': 188, 'start': 187,
                'label': 'días arl',
                'type': 'N', 'long': '2'},
            {'field': '39', 'end': 190, 'start': 189,
                'label': 'días caja',
                'type': 'N', 'long': '2'},
            {'field': '40', 'end': 199, 'start': 191,
                'label': 'Salario básico',
                'type': 'N', 'long': '9'},
            {'field': '41', 'end': 200, 'start': 200,
                'label': 'Salario integra',
                'type': 'A', 'long': '1'},
            {'field': '42', 'end': 209, 'start': 201,
                'label': 'IBC pensión',
                'type': 'N', 'long': '9'},
            {'field': '43', 'end': 218, 'start': 210,
                'label': 'IBC salud',
                'type': 'N', 'long': '9'},
            {'field': '44', 'end': 227, 'start': 219,
                'label': 'IBC arl',
                'type': 'N', 'long': '9'},
            {'field': '45', 'end': 236, 'start': 228,
                'label': 'IBC caja',
                'type': 'N', 'long': '9'},
            {'field': '46', 'end': 243, 'start': 237,
                'label': 'Tarifa pension',
                'type': 'N', 'long': '7'},
            {'field': '47', 'end': 252, 'start': 244,
                'label': 'Cotización obligatoria a pensiones',
                'type': 'N', 'long': '9'},
            {'field': '48', 'end': 261, 'start': 253,
                'label': 'Aporte voluntario del afiliado a pensiones',
                'type': 'N', 'long': '9'},
            {'field': '49', 'end': 270, 'start': 262,
                'label': 'Aporte voluntario del aportante a pensiones',
                'type': 'N', 'long': '9'},
            {'field': '50', 'end': 279, 'start': 271,
                'label': 'Total cotización pensiones',
                'type': 'N', 'long': '9'},
            {'field': '51', 'end': 288, 'start': 280,
                'label': 'Solidaridad',
                'type': 'N', 'long': '9'},
            {'field': '52', 'end': 297, 'start': 289,
                'label': 'Subsistencia',
                'type': 'N', 'long': '9'},
            {'field': '53', 'end': 306, 'start': 298,
                'label': 'Valor no retenido por aportes voluntarios',
                'type': 'N', 'long': '9'},
            {'field': '54', 'end': 313, 'start': 307,
                'label': 'Tarifa salud',
                'type': 'N', 'long': '7'},
            {'field': '55', 'end': 322, 'start': 314,
                'label': 'Cotización obligatoria a salud',
                'type': 'N', 'long': '9'},
            {'field': '56', 'end': 331, 'start': 323,
                'label': 'Valor de la UPC adicional',
                'type': 'N', 'long': '9'},
            {'field': '57', 'end': 346, 'start': 332,
                'label': 'N° autorización incapacidad por enfermedad general',
                'type': 'A', 'long': '15'},
            {'field': '58', 'end': 355, 'start': 347,
                'label': 'Valor de la incapacidad por enfermedad general',
                'type': 'N', 'long': '9'},
            {'field': '59', 'end': 370, 'start': 356,
                'label': 'N° autorización lic maternidad o paternidad',
                'type': 'A', 'long': '15'},
            {'field': '60', 'end': 379, 'start': 371,
                'label': 'Valor lic de maternidad',
                'type': 'N', 'long': '9'},
            {'field': '61', 'end': 388, 'start': 380,
                'label': 'Tarifa arl',
                'type': 'N', 'long': '9'},
            {'field': '62', 'end': 397, 'start': 389,
                'label': 'Centro de trabajo CT',
                'type': 'N', 'long': '9'},
            {'field': '63', 'end': 406, 'start': 398,
                'label': 'Cotización arl',
                'type': 'N', 'long': '9'},
            {'field': '64', 'end': 413, 'start': 407,
                'label': 'Tarifa caja',
                'type': 'N', 'long': '7'},
            {'field': '65', 'end': 422, 'start': 414,
                'label': 'Valor caja',
                'type': 'N', 'long': '9'},
            {'field': '66', 'end': 429, 'start': 423,
                'label': 'Tarifa de aportes SENA',
                'type': 'N', 'long': '7'},
            {'field': '67', 'end': 438, 'start': 430,
                'label': 'Valor aportes SENA',
                'type': 'N', 'long': '9'},
            {'field': '68', 'end': 445, 'start': 439,
                'label': 'Tarifa aportes ICBF',
                'type': 'N', 'long': '7'},
            {'field': '69', 'end': 454, 'start': 446,
                'label': 'Valor aporte ICBF',
                'type': 'N', 'long': '9'},
            {'field': '70', 'end': 461, 'start': 455,
                'label': 'Tarifa aportes ESAP',
                'type': 'N', 'long': '7'},
            {'field': '71', 'end': 470, 'start': 462,
                'label': 'Valor aporte ESAP',
                'type': 'N', 'long': '9'},
            {'field': '72', 'end': 477, 'start': 471,
                'label': 'Tarifa aportes MEN',
                'type': 'N', 'long': '7'},
            {'field': '73', 'end': 486, 'start': 478,
                'label': 'Valor aporte MEN',
                'type': 'N', 'long': '9'},
            {'field': '74', 'end': 488, 'start': 487,
                'label': 'Tipo de documento del cotizante principal',
                'type': 'A', 'long': '2'},
            {'field': '75', 'end': 504, 'start': 489,
                'label': 'Número de identificación del cotizante principal',
                'type': 'A', 'long': '16'},
            {'field': '76', 'end': 505, 'start': 505,
                'label': 'Cotizante exonerado pago aporte salud SENA e ICBF',
                'type': 'A', 'long': '1'},
            {'field': '77', 'end': 511, 'start': 506,
                'label': 'Código arl',
                'type': 'A', 'long': '6'},
            {'field': '78', 'end': 512, 'start': 512,
                'label': 'Clase de riesgo',
                'type': 'A', 'long': '1'},
            {'field': '79', 'end': 513, 'start': 513,
                'label': 'Indicador tarifa especial pensiones',
                'type': 'A', 'long': '1'},
            {'field': '80', 'end': 523, 'start': 514,
                'label': 'Fecha de ingreso',
                'type': 'A', 'long': '10'},
            {'field': '81', 'end': 533, 'start': 524,
                'label': 'Fecha de retiro',
                'type': 'A', 'long': '10'},
            {'field': '82', 'end': 543, 'start': 534,
                'label': 'Fecha Inicio VSP',
                'type': 'A', 'long': '10'},
            {'field': '83', 'end': 553, 'start': 544,
                'label': 'Fecha Inicio SLN',
                'type': 'A', 'long': '10'},
            {'field': '84', 'end': 563, 'start': 554,
                'label': 'Fecha fin SLN',
                'type': 'A', 'long': '10'},
            {'field': '85', 'end': 573, 'start': 564,
                'label': 'Fecha inicio IGE',
                'type': 'A', 'long': '10'},
            {'field': '86', 'end': 583, 'start': 574,
                'label': 'Fecha fin IGE',
                'type': 'A', 'long': '10'},
            {'field': '87', 'end': 593, 'start': 584,
                'label': 'Fecha inicio LMA',
                'type': 'A', 'long': '10'},
            {'field': '88', 'end': 603, 'start': 594,
                'label': 'Fecha fin LMA',
                'type': 'A', 'long': '10'},
            {'field': '89', 'end': 613, 'start': 604,
                'label': 'Fecha inicio VAC - LR',
                'type': 'A', 'long': '10'},
            {'field': '90', 'end': 623, 'start': 614,
                'label': 'Fecha fin VAC - LR',
                'type': 'A', 'long': '10'},
            {'field': '91', 'end': 633, 'start': 624,
                'label': 'Fecha inicio VCT',
                'type': 'A', 'long': '10'},
            {'field': '92', 'end': 643, 'start': 634,
                'label': 'Fecha fin VCT',
                'type': 'A', 'long': '10'},
            {'field': '93', 'end': 653, 'start': 644,
                'label': 'Fecha inicio IRL',
                'type': 'A', 'long': '10'},
            {'field': '94', 'end': 663, 'start': 654,
                'label': 'Fecha fin IRL',
                'type': 'A', 'long': '10'},
            {'field': '95', 'end': 672, 'start': 664,
                'label': 'IBC otros parafiscales diferentes a CCF',
                'type': 'N', 'long': '9'},
            {'field': '96', 'end': 675, 'start': 673,
                'label': 'N horas laboradas',
                'type': 'N', 'long': '3'}
        ]

    def _set_field_zero(self, new_line, _fields, rows, value=0):
        for row in rows:
            new_line[row] = str(self.set_data_field(_fields[row], str(value)))

    def _get_data_lines(self, line_ids):
        total = 0
        days = 0
        date_start = False
        date_end = False
        for line in line_ids:
            if not line.payroll_news_id:
                continue
            days += abs(line.quantity)
            total += abs(line.total)
            if date_start is False or date_start > line.\
                    payroll_news_id[0].request_date_from:
                date_start = line.payroll_news_id[0].request_date_from

            if date_end is False or date_end < line.\
                    payroll_news_id[0].request_date_to:
                date_end = line.payroll_news_id[0].request_date_to
        return total, days, date_start, date_end

    # LISTO
    # PENDIENTE 30 DIAS
    def _generate_sln_lines(self, payslip, sequence, localdict,
                            basic_info, line_ids, _fields, res):
        total, days, date_start, date_end = self._get_data_lines(line_ids)
        if total == 0 or days == 0:
            return

        sequence += 1
        new_line = basic_info.copy()
        new_line[1] = self.compute_field_2(
            _fields[1],
            payslip, sequence, localdict)

        # Marcar la novedad
        new_line[20] = str(self.set_data_field(_fields[20], ''))
        new_line[22] = str(self.set_data_field(_fields[22], ''))
        new_line[27] = str(self.set_data_field(_fields[27], ''))
        new_line[23] = str(self.set_data_field(_fields[23], 'X'))
        new_line[35] = self.compute_field_36(
            _fields[35],
            payslip, sequence, localdict, days)

        new_line[36] = self.compute_field_37(
            _fields[36],
            payslip, sequence, localdict, days)
        new_line[37] = self.compute_field_38(
            _fields[37],
            payslip, sequence, localdict, days)
        new_line[38] = self.compute_field_39(
            _fields[38],
            payslip, sequence, localdict, days)

        # IBC
        ibc = math.ceil(
            total*0.7 if localdict.get('is_integral', False) else total)
        self._set_field_zero(
            new_line, _fields,
            [41, 42, 43, 44, 94], int(ibc))
        localdict['field_42'] = int(ibc)
        # FIN IBC

        # INICIO TARIFA
        new_line[45] = self.compute_field_46(
            _fields[45], payslip, sequence,
            localdict, ['PENS'])

        new_line[53] = self.compute_field_54(
            _fields[53], payslip, sequence,
            localdict, ['SALU'])

        localdict['field_43'] = int(ibc)
        new_line[54] = self.compute_field_55(
            _fields[54], payslip, sequence,
            localdict)

        self._set_field_zero(
            new_line, _fields,
            [60, 63, 65, 67, 69, 71])
        # FIN TARIFA

        # INICIO TOTAL COTIZACION
        new_line[46] = self.compute_field_47(
            _fields[46], payslip, sequence,
            localdict)
        self._set_field_zero(
            new_line, _fields,
            [50, 51, 62, 64, 66, 68, 70, 72])
        # FIN TOTAL COTIZACION

        localdict['field_48'] = 0
        localdict['field_49'] = 0
        new_line[49] = self.compute_field_50(
            _fields[49], payslip, sequence, localdict)

        new_line[82] = self._get_date_fields(
            _fields[82], date_start)
        new_line[83] = self._get_date_fields(
            _fields[83], date_end)
        res.append(new_line)

    # LISTO
    # PENDIENTE 30 DIAS
    def _generate_ige_lines(self, payslip, sequence, localdict,
                            basic_info, line_ids, _fields, res):
        total, days, date_start, date_end = self._get_data_lines(line_ids)
        if total == 0 or days == 0:
            return

        ibc = basic_info[43]
        self._set_field_zero(
            basic_info, _fields,
            [41, 42, 43, 44], int(ibc))
        self._set_field_zero(
            basic_info, _fields,
            [41, 42, 43, 44], int(ibc))
        localdict['field_42'] = int(ibc)
        # INICIO TOTAL COTIZACION
        basic_info[46] = self.compute_field_47(
            _fields[46], payslip, sequence,
            localdict)

        localdict['field_43'] = int(ibc)
        localdict['field_55_calculate'] = True
        basic_info[54] = self.compute_field_55(
            _fields[54], payslip, sequence,
            localdict)

        localdict['field_44'] = int(ibc)
        localdict['field_63_calculate'] = False
        basic_info[62] = self.compute_field_63(
            _fields[62], payslip, sequence,
            localdict)

        localdict['field_45'] = int(ibc)
        basic_info[64] = self.compute_field_65(
            _fields[64], payslip, sequence,
            localdict)

        # FIN IBC
        sequence += 1
        new_line = basic_info.copy()
        new_line[1] = self.compute_field_2(
            _fields[1],
            payslip, sequence, localdict)

        # Marcar la novedad
        new_line[20] = str(self.set_data_field(_fields[20], ''))
        new_line[22] = str(self.set_data_field(_fields[22], ''))
        new_line[27] = str(self.set_data_field(_fields[27], ''))
        new_line[24] = str(self.set_data_field(_fields[24], 'X'))

        new_line[35] = self.compute_field_36(
            _fields[35],
            payslip, sequence, localdict, days)

        new_line[36] = self.compute_field_37(
            _fields[36],
            payslip, sequence, localdict, days)
        new_line[37] = self.compute_field_38(
            _fields[37],
            payslip, sequence, localdict, days)
        new_line[38] = self.compute_field_39(
            _fields[38],
            payslip, sequence, localdict, days)

        # IBC
        ibc = math.ceil(total*0.7 if localdict.get('is_integral', False)
                        else total)
        self._set_field_zero(
            new_line, _fields,
            [41, 42, 43, 44, 94], int(ibc))
        localdict['field_42'] = int(ibc)
        localdict['field_43'] = int(ibc)
        new_line[54] = self.compute_field_55(
            _fields[54], payslip, sequence,
            localdict)

        self._set_field_zero(
            new_line, _fields,
            [60, 63, 65, 67, 69, 71])
        # FIN TARIFA

        # INICIO TOTAL COTIZACION
        new_line[46] = self.compute_field_47(
            _fields[46], payslip, sequence,
            localdict)
        self._set_field_zero(
            new_line, _fields,
            [50, 51, 62, 64, 66, 68, 70, 72, 47])

        localdict['field_48'] = 0
        localdict['field_49'] = 0
        new_line[49] = self.compute_field_50(
            _fields[49], payslip, sequence, localdict)

        # FIN TOTAL COTIZACION

        new_line[84] = self._get_date_fields(
            _fields[84], date_start)
        new_line[85] = self._get_date_fields(
            _fields[85], date_end)
        res.append(new_line)

    # LISTO
    # PENDIENTE 30 DIAS
    def _generate_lma_lines(self, payslip, sequence, localdict,
                            basic_info, line_ids, _fields, res):
        total, days, date_start, date_end = self._get_data_lines(line_ids)
        if total == 0 or days == 0:
            return

        if days >= 30:
            basic_info[22] = str(self.set_data_field(_fields[22], ''))
            basic_info[25] = str(self.set_data_field(_fields[25], 'X'))
            basic_info[86] = self._get_date_fields(
                _fields[86], date_start)
            basic_info[87] = self._get_date_fields(
                _fields[87], date_end)
            self._set_field_zero(
                basic_info, _fields,
                [35, 36, 37, 38], int(total))
            return

        ibc = basic_info[43]
        self._set_field_zero(
            basic_info, _fields,
            [41, 42, 43, 44], int(ibc))
        localdict['field_42'] = int(ibc)
        # INICIO TOTAL COTIZACION
        basic_info[46] = self.compute_field_47(
            _fields[46], payslip, sequence,
            localdict)

        localdict['field_43'] = int(ibc)
        localdict['field_55_calculate'] = True
        basic_info[54] = self.compute_field_55(
            _fields[54], payslip, sequence,
            localdict)

        localdict['field_44'] = int(ibc)
        localdict['field_63_calculate'] = False
        basic_info[62] = self.compute_field_63(
            _fields[62], payslip, sequence,
            localdict)

        localdict['field_45'] = int(ibc)

        basic_info[64] = self.compute_field_65(
            _fields[64], payslip, sequence,
            localdict)

        # FIN IBC

        new_line = basic_info.copy()
        sequence += 1
        new_line[1] = self.compute_field_2(
            _fields[1],
            payslip, sequence, localdict)

        # Marcar la novedad
        new_line[22] = str(self.set_data_field(_fields[22], ''))
        new_line[27] = str(self.set_data_field(_fields[27], ''))
        new_line[25] = str(self.set_data_field(_fields[25], 'X'))

        new_line[35] = self.compute_field_36(
            _fields[35],
            payslip, sequence, localdict, days)

        new_line[36] = self.compute_field_37(
            _fields[36],
            payslip, sequence, localdict, days)
        new_line[37] = self.compute_field_38(
            _fields[37],
            payslip, sequence, localdict, days)
        new_line[38] = self.compute_field_39(
            _fields[38],
            payslip, sequence, localdict, days)

        # IBC
        ibc = total*0.7 if localdict.get('is_integral', False)\
            else total
        self._set_field_zero(
            new_line, _fields,
            [41, 42, 43, 44, 94], int(ibc))
        localdict['field_42'] = int(ibc)
        # FIN IBC

        # INICIO TARIFA
        new_line[45] = self.compute_field_46(
            _fields[45], payslip, sequence,
            localdict)

        new_line[53] = self.compute_field_54(
            _fields[53], payslip, sequence,
            localdict)

        localdict['field_43'] = int(ibc)
        new_line[54] = self.compute_field_55(
            _fields[54], payslip, sequence,
            localdict)

        self._set_field_zero(
            new_line, _fields,
            [60, 69, 71])
        # FIN TARIFA

        # INICIO TOTAL COTIZACION
        new_line[46] = self.compute_field_47(
            _fields[46], payslip, sequence,
            localdict)

        localdict['field_44'] = int(ibc)
        localdict['field_61'] = int(0)
        new_line[62] = self.compute_field_63(
            _fields[62], payslip, sequence,
            localdict)

        localdict['field_45'] = int(ibc)
        new_line[64] = self.compute_field_65(
            _fields[64], payslip, sequence,
            localdict)

        new_line[86] = self._get_date_fields(
            _fields[86], date_start)
        new_line[87] = self._get_date_fields(
            _fields[87], date_end)
        codes = self.get_config_rules(payslip, 'non_apply_box_rule_ids')
        if codes > 0:
            self._set_field_zero(
                new_line, _fields,
                [63, 64])

        res.append(new_line)

    def last_day_of_month(self, date):
        if date.month == 12:
            return date.replace(day=31)
        return date.replace(month=date.month+1, day=1) - timedelta(days=1)

    # Probar con el modulo de VAC
    # Verificar si se puede liquidar Vacaciones y Lic remuneradas en el mismo
    # periodo
    def _generate_vac_lr_lines(self, payslip, sequence, localdict,
                               basic_info, line_ids, _fields, res):
        nov = 'X' if not localdict.get('IS_LR', False) else 'L'
        total, days, date_start, date_end = self._get_data_lines(line_ids)
        if total == 0 or days == 0:
            return

        codes = self.get_config_rules(
            payslip, 'ibc_adjustment_rule_ids', line_ids=True)
        lines = payslip.line_ids.filtered(lambda line: line.id in codes)
        total2 = total + sum([line.amount for line in lines]) or 0

        last_day = self.last_day_of_month(date_start)
        if date_end > last_day:
            date_end = last_day
        if days >= 30:
            basic_info[22] = str(self.set_data_field(_fields[22], ''))
            basic_info[26] = str(self.set_data_field(_fields[26], nov))
            basic_info[86] = self._get_date_fields(
                _fields[86], date_start)
            basic_info[87] = self._get_date_fields(
                _fields[87], date_end)
            self._set_field_zero(
                basic_info, _fields,
                [35, 36, 37, 38], int(total))
            return

        ibc = basic_info[43]
        self._set_field_zero(
            basic_info, _fields,
            [41, 42, 43, 44], int(ibc))
        localdict['field_42'] = int(ibc)
        # INICIO TOTAL COTIZACION
        basic_info[46] = self.compute_field_47(
            _fields[46], payslip, sequence,
            localdict)
        localdict['field_47'] = basic_info[46]
        localdict['field_43'] = int(ibc)
        localdict['field_55_calculate'] = True
        basic_info[54] = self.compute_field_55(
            _fields[54], payslip, sequence,
            localdict)

        localdict['field_44'] = int(ibc)
        localdict['field_63_calculate'] = False
        basic_info[62] = self.compute_field_63(
            _fields[62], payslip, sequence,
            localdict)

        localdict['field_45'] = int(ibc)

        basic_info[64] = self.compute_field_65(
            _fields[64], payslip, sequence,
            localdict)

        basic_info[49] = self.compute_field_50(
            _fields[49], payslip, sequence, localdict)

        _user = self.env['ir.config_parameter'].sudo()
        rate1 = float(_user.get_param('hr_payroll.rate_subsistence_afs'))
        rate2 = float(_user.get_param('hr_payroll.rate_solidarity_afs'))
        if localdict.get('field_51', 0) > 0 and \
           localdict.get('field_52', 0) > 0:
            field_51 = int((int(ibc)*(rate1/100))/100)
            field_51_ibc = int(
                (localdict.get('field_51_ibc', 1)/30) * (30-days))
            basic_info[50] = str(
                self.set_data_field(_fields[50], str(field_51)))
            field_52 = int((int(ibc)*(rate2/100))/100)
            basic_info[51] = str(
                self.set_data_field(_fields[51], str(field_52)))

        # FIN IBC

        new_line = basic_info.copy()
        sequence += 1
        new_line[1] = self.compute_field_2(
            _fields[1],
            payslip, sequence, localdict)

        # Marcar la novedad
        new_line[20] = str(self.set_data_field(_fields[20], ''))
        new_line[22] = str(self.set_data_field(_fields[22], ''))
        new_line[27] = str(self.set_data_field(_fields[27], ''))
        new_line[26] = str(self.set_data_field(_fields[26], nov))

        new_line[35] = self.compute_field_36(
            _fields[35],
            payslip, sequence, localdict, days)

        new_line[36] = self.compute_field_37(
            _fields[36],
            payslip, sequence, localdict, days)
        new_line[37] = self.compute_field_38(
            _fields[37],
            payslip, sequence, localdict, days)
        new_line[38] = self.compute_field_39(
            _fields[38],
            payslip, sequence, localdict, days)

        # IBC
        ibc = total*0.7 if localdict.get('is_integral', False)\
            else total
        ibc2 = total2*0.7 if localdict.get('is_integral', False)\
            else total2
        self._set_field_zero(
            new_line, _fields,
            [44, 94], int(ibc))
        self._set_field_zero(
            new_line, _fields,
            [41, 42, 43], int(ibc2))
        localdict['field_42'] = int(ibc2)
        # FIN IBC

        # INICIO TARIFA
        new_line[45] = self.compute_field_46(
            _fields[45], payslip, sequence,
            localdict)

        new_line[53] = self.compute_field_54(
            _fields[53], payslip, sequence,
            localdict)

        localdict['field_43'] = int(ibc2)
        new_line[54] = self.compute_field_55(
            _fields[54], payslip, sequence,
            localdict)

        self._set_field_zero(
            new_line, _fields,
            [60, 69, 71])
        # FIN TARIFA

        if localdict.get('field_51', 0) > 0 and \
           localdict.get('field_52', 0) > 0:
            field_51 = int((int(ibc2)*(rate1/100))/100)
            new_line[50] = str(self.set_data_field(_fields[50], str(field_51)))
            field_52 = int((int(ibc2)*(rate2/100))/100)
            new_line[51] = str(self.set_data_field(_fields[51], str(field_52)))

        # INICIO TOTAL COTIZACION
        new_line[46] = self.compute_field_47(
            _fields[46], payslip, sequence,
            localdict)

        localdict['field_47'] = new_line[46]
        new_line[49] = self.compute_field_50(
            _fields[49], payslip, sequence, localdict)

        localdict['field_44'] = int(ibc2)
        localdict['field_61'] = int(0)
        new_line[62] = self.compute_field_63(
            _fields[62], payslip, sequence,
            localdict)

        localdict['field_45'] = int(ibc)
        new_line[64] = self.compute_field_65(
            _fields[64], payslip, sequence,
            localdict)

        new_line[88] = self._get_date_fields(
            _fields[88], date_start)
        new_line[89] = self._get_date_fields(
            _fields[89], date_end)

        codes = self.get_config_rules(payslip, 'non_apply_box_rule_ids')
        if codes > 0:
            self._set_field_zero(
                new_line, _fields,
                [63, 64])

        res.append(new_line)

    # PENDIENTE
    def _generate_irl_lines(self, payslip, sequence, localdict,
                            basic_info, line_ids, _fields, res):
        total, days, date_start, date_end = self._get_data_lines(line_ids)
        if total == 0 or days == 0:
            return

        if days >= 30:
            basic_info[22] = str(self.set_data_field(_fields[22], ''))
            basic_info[29] = str(self.set_data_field(_fields[29], 'X'))
            basic_info[92] = self._get_date_fields(
                _fields[92], date_start)
            basic_info[93] = self._get_date_fields(
                _fields[93], date_end)
            self._set_field_zero(
                basic_info, _fields,
                [35, 36, 37, 38], int(total))
            return

        ibc = basic_info[43]
        self._set_field_zero(
            basic_info, _fields,
            [41, 42, 43, 44], int(ibc))
        localdict['field_42'] = int(ibc)
        # INICIO TOTAL COTIZACION
        basic_info[46] = self.compute_field_47(
            _fields[46], payslip, sequence,
            localdict)

        localdict['field_43'] = int(ibc)
        localdict['field_55_calculate'] = True
        basic_info[54] = self.compute_field_55(
            _fields[54], payslip, sequence,
            localdict)

        localdict['field_44'] = int(ibc)
        basic_info[62] = self.compute_field_63(
            _fields[62], payslip, sequence,
            localdict)

        localdict['field_45'] = int(ibc)

        basic_info[64] = self.compute_field_65(
            _fields[64], payslip, sequence,
            localdict)
        # FIN IBC

        new_line = basic_info.copy()
        sequence += 1
        new_line[1] = self.compute_field_2(
            _fields[1],
            payslip, sequence, localdict)

        # Marcar la novedad
        new_line[22] = str(self.set_data_field(_fields[22], ''))
        new_line[27] = str(self.set_data_field(_fields[27], ''))
        new_line[29] = str(self.set_data_field(_fields[29], 'X'))

        new_line[35] = self.compute_field_36(
            _fields[35],
            payslip, sequence, localdict, days)

        new_line[36] = self.compute_field_37(
            _fields[36],
            payslip, sequence, localdict, days)
        new_line[37] = self.compute_field_38(
            _fields[37],
            payslip, sequence, localdict, days)
        new_line[38] = self.compute_field_39(
            _fields[38],
            payslip, sequence, localdict, days)

        # IBC
        ibc = total*0.7 if localdict.get('is_integral', False)\
            else total
        self._set_field_zero(
            new_line, _fields,
            [41, 42, 43, 44, 94], int(ibc))
        localdict['field_42'] = int(ibc)
        # FIN IBC

        # INICIO TARIFA
        new_line[45] = self.compute_field_46(
            _fields[45], payslip, sequence,
            localdict)

        new_line[53] = self.compute_field_54(
            _fields[53], payslip, sequence,
            localdict)

        localdict['field_43'] = int(ibc)
        new_line[54] = self.compute_field_55(
            _fields[54], payslip, sequence,
            localdict)

        self._set_field_zero(
            new_line, _fields,
            [60, 69, 71])
        # FIN TARIFA

        # INICIO TOTAL COTIZACION
        new_line[46] = self.compute_field_47(
            _fields[46], payslip, sequence,
            localdict)

        localdict['field_44'] = int(ibc)
        localdict['field_61'] = int(0)
        new_line[62] = self.compute_field_63(
            _fields[62], payslip, sequence,
            localdict)

        localdict['field_45'] = int(ibc)
        new_line[64] = self.compute_field_65(
            _fields[64], payslip, sequence,
            localdict)

        new_line[92] = self._get_date_fields(
            _fields[92], date_start)
        new_line[93] = self._get_date_fields(
            _fields[93], date_end)
        res.append(new_line)

    def _generate_payroll_news_lines(self, row, payslip, sequence,
                                     localdict, basic_info):
        res = []
        _fields = self._get_data_fields()

        # SLN: Suspencion temporal del contrato laboral o
        # licencia no remunerada o comision de servicios
        # compute_field_24
        if localdict.get('SLN', False):
            sln = localdict.get('SLN')
            line_ids = self.env['hr.payslip.line'].browse(sln.get('ids'))
            self._generate_sln_lines(
                payslip, sequence, localdict, basic_info,
                line_ids, _fields, res)

        # IGE: Incapacidad temporal por enfermedad general
        # compute_field_25
        if localdict.get('IGE', False):
            ige = localdict.get('IGE')
            line_ids = self.env['hr.payslip.line'].browse(ige.get('ids'))
            self._generate_ige_lines(
                payslip, sequence, localdict, basic_info,
                line_ids, _fields, res)

        # LMA: Licencia de maternidad o de Paternidad
        # compute_field_26
        if localdict.get('LMA', False):
            lma = localdict.get('LMA')
            line_ids = self.env['hr.payslip.line'].browse(lma.get('ids'))
            self._generate_lma_lines(
                payslip, sequence, localdict, basic_info,
                line_ids, _fields, res)

        # VAC - LR: Vacaciones, Licencia remunerada
        # compute_field_27
        if localdict.get('VAC_LR', False):
            vac_lr = localdict.get('VAC_LR')
            line_ids = self.env['hr.payslip.line'].browse(vac_lr.get('ids'))
            lr_ids = line_ids.filtered(lambda line: line.code == '26')
            localdict.update(IS_LR=(bool)(len(lr_ids) > 0))
            self._generate_vac_lr_lines(
                payslip, sequence, localdict, basic_info,
                line_ids, _fields, res)

        # IRL: Dias de incapacidad por accidente de trabajo
        # compute_field_30
        if localdict.get('IRL', False):
            irl = localdict.get('IRL')
            line_ids = self.env['hr.payslip.line'].browse(irl.get('ids'))
            self._generate_irl_lines(
                payslip, sequence, localdict, basic_info,
                line_ids, _fields, res)

        return res

    def _get_body_file_parafiscal(self):
        body = ''
        header = ''
        total = []
        if self.env.context.get('active_model') == 'account.payment':
            payment = self.env['account.payment'].browse(
                self.env.context['active_id'])
            lines = payment.move_line_ids.filtered('debit')
            _ids = []
            for line in lines:
                res = line.full_reconcile_id\
                    .reconciled_line_ids.filtered('credit')
                _ids += self.env['hr.payslip'].search(
                    [('move_id.id', 'in', res.move_id.ids)])
            sequence = 1
            payslip_ids = set(_ids)
            if len(payslip_ids) == 0:
                return bytes(body, 'utf8'), total
            localarray = []
            _fields = self._get_data_fields()
            for payslip_id in payslip_ids:
                row_data = ''
                basic_info = []
                localdict = dict()
                lines = payslip_id.line_ids.filtered(
                    lambda line: line.code == 'BASIC')
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
                if len_adi > 0:
                    localarray += aditional
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

    def get_collect_data_parafiscal(self):
        body, total = self._get_body_file_parafiscal()
        if not self.file_extension == 'csv':
            header = self._get_header_file_parafiscal(total)
            return header + body
        return body
