from odoo import api, fields, models, _
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

import csv
import base64
from io import BytesIO
from odoo.exceptions import UserError, ValidationError


FIRST_COLUMNS_AMOUNT = 4
END_COLUMNS_AMOUNT = 0
NAME_TOTAL = "Sueldo Promedio"
DAYS_COLUMN = "DIAS LABORADOS"
EMPLOYEE_COLUMN = "EMPLEADO"
GREAT_STATUS = "done"


class PayrollProvisionsReport(models.Model):

    _name = 'payroll.provisions.report'
    _description = _('Provision reporting module')

    date_start = fields.Date(
        string='Initial date',
        tracking=True)
    date_end = fields.Date(
        string='End date', tracking=True)
    employees = fields.Many2one(
        'hr.employee',
        string="Employees",
        index=True, tracking=True)
    all_employees = fields.Boolean(
        string="All employees",
        default=False)

    file_filename = fields.Char('File Names')
    file_binary = fields.Binary(string='File')
    file_extension = fields.Selection(
        string='File extension',
        selection=[
            ('csv', 'CSV'),
            ('txt', 'TXT'),
            ('xls', 'EXCEL')
        ],
        default='xls')
    necesary_rows = [
        {
            "N°": "SUELDO",
            "TIPO": "NORMAL",
            "DIAS LABORADOS": 360,
            "RULE": "salary_provision_rule",
            "CALC": "salary"
        }, {
            "N°": "COMIS + HE",
            "TIPO": "NORMAL",
            "DIAS LABORADOS": 360,
            "RULE": "overtime_provision_rule",
            "CALC": "sum"
        }, {
            "N°": "AJUSTE",
            "TIPO": "NORMAL",
            "DIAS LABORADOS": 360,
            "RULE": "adjustment_provision_rule",
            "CALC": "average"
        }, {
            "N°": "AJUSTE DE CIERRE",
            "TIPO": "NORMAL",
            "DIAS LABORADOS": 360,
            "RULE": "closing_adjustment_provision_rule",
            "CALC": "sum"
        }, {
            "N°": "PROVISION PRIMA",
            "TIPO": "NORMAL",
            "DIAS LABORADOS": 360,
            "RULE": "bonus_provision_rule",
            "CALC": "average"
        }, {
            "N°": "PROVISION CESANTIAS",
            "TIPO": "NORMAL",
            "DIAS LABORADOS": 360,
            "RULE": "provision_rule",
            "CALC": "sum"
        }, {
            "N°": "PROVICION VACACIONES",
            "TIPO": "NORMAL",
            "DIAS LABORADOS": 360,
            "RULE": "vacations_provision_rule",
            "CALC": "average"
        }
    ]

    def get_rule_data(self, rule):
        obtained_rules = self.env['ir.config_parameter'].sudo()\
                .get_param('many2many.' + rule)
        obtained_rules = "[]" if not obtained_rules else obtained_rules
        result = []
        for obtained_rule in eval(obtained_rules):
            result.append(
                self.env['hr.salary.rule'].browse(obtained_rule).code
            )
        return result

    def get_payslips_data(self):
        if self.all_employees:
            return self.env['hr.payslip'].search([
                ('date_from', '>=', self.date_start),
                ('date_to', '<=', self.date_end),
                ('state', '=', GREAT_STATUS)
            ])
        return self.env['hr.payslip'].search([
            ('employee_id', '=', self.employees.id),
            ('date_from', '>=', self.date_start),
            ('date_to', '<=', self.date_end),
            ('state', '=', GREAT_STATUS)
        ])

    def create_column_name(self, date):
        return date.strftime('%y/%m')

    def create_structure(self, column_relation, row_copy, result_data):
        date_iteration = self.date_start
        quantity = FIRST_COLUMNS_AMOUNT
        while date_iteration <= self.date_end:
            column_name = self.create_column_name(date_iteration)
            column_relation[column_name] = quantity
            row_copy.append("")
            quantity += 1
            date_iteration = date_iteration + relativedelta(months=+1)
        row_copy.append("")
        result_data = self.create_titles(
            column_relation, row_copy.copy(), result_data)
        return self.get_format_data(column_relation, row_copy, result_data)

    def create_titles(self, column_relation, row, result_data):
        for key, value in column_relation.items():
            row[value] = key
        result_data.append(row)
        return result_data

    def create_row(
                    self, employees_line_ids, column_relation,
                    row_copy, result_data):
        for key_payslips, payslips in employees_line_ids.items():
            days_quantity = 0
            for i in self.necesary_rows:
                row = row_copy.copy()
                employee = ""
                for key, value in i.items():
                    if key != "RULE" and key != "CALC":
                        row[column_relation[key]] = value
                for payslip in payslips:
                    employee = payslip["employee_id"].name
                    column_name = self.create_column_name(payslip.date_from)
                    column_name = column_relation[column_name]
                    line_ids = payslip["line_ids"]
                    rules = self.get_rule_data(i.get("RULE"))
                    result = 0
                    for rule in rules:
                        for line_id in line_ids:
                            if line_id["code"] == rule:
                                result += line_id["total"]
                                if i.get("N°") == "SUELDO":
                                    days_quantity += line_id["quantity"]
                    if result != 0:
                        row[column_name] = result
                row[column_relation[EMPLOYEE_COLUMN]] = employee
                row[column_relation[DAYS_COLUMN]] = days_quantity
                result_data.append(row)
        return result_data

    def get_data(self, column_relation, row_copy, result_data):
        payslips = self.get_payslips_data()
        employees_line_ids = {}
        for payslip in payslips:
            if not employees_line_ids.get(payslip["employee_id"].id, False):
                employees_line_ids[payslip["employee_id"].id] = []
            employees_line_ids[payslip["employee_id"].id].append(payslip)
        result_data = self.create_row(
            employees_line_ids, column_relation, row_copy, result_data)
        return bytes(self.create_view(result_data), 'utf8')

    def create_view(self, result_data):
        data = ""
        for row in result_data:
            row_data = ""
            for cell in row:
                row_data += ";" + str(cell) if row_data != "" else str(cell)
            data += row_data + "\n"
        return data

    def get_format_data(self, column_relation, row_copy, result_data):
        get_data = self.get_data(column_relation, row_copy, result_data)
        file_output = BytesIO(get_data)
        file_output.seek(0)
        return file_output.read()

    def generate_excel_report(self):
        column_relation = {
            "N°": 0,
            "TIPO": 1,
            "DIAS LABORADOS": 2,
            "EMPLEADO": 3,
        }
        row_copy = [
            "",
            "",
            ""
        ]
        result_data = []

        get_data = self.create_structure(
            column_relation, row_copy, result_data)

        context = self.env.context
        self.write({
            'file_filename': '{0}.{1}'.format(
                'file', self.file_extension),
            'file_binary': base64.b64encode(get_data)
        })
        return {
            'context': context,
            'name': _("Provisions Report"),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'payroll.provisions.report',
            'res_id': self.id,
            'view_id': self.env.ref('payroll_provisions_report.'
                                    'payroll_provisions_report_form').id,
            'type': 'ir.actions.act_window',
            'target': 'new',
        }
