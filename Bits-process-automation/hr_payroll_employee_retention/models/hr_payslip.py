from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from dateutil.relativedelta import relativedelta
from datetime import datetime, date
import calendar
from odoo.addons.hr_payroll.models.browsable_object \
    import BrowsableObject, InputLine, WorkedDays, Payslips


class Retention(BrowsableObject):

    def compute_employee_retention(self, codes, from_date, to_date):
        return self.dict._get_withholding_tax_calculation() or 0.0


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    line_ids_compute = fields.Many2many(
        'hr.payslip.line',
        store=False
    )

    def _get_base_local_dict(self):
        employee = self.employee_id
        res = super()._get_base_local_dict()
        res.update({
            'retention': Retention(employee.id, self, self.env)
        })
        return res

    def _get_retention_source_item(self, code):
        return self.env['hr.payroll.retention'].search(
            [('code', '=', code)])

    def _get_lines_payslip_dict(self):

        list_lines = self.line_ids_compute.read([
            'name', 'code', 'category_id', 'quantity',
            'rate', 'salary_rule_id', 'amount', 'total'])

        dict_payslip_lines = {}
        for list_line in list_lines:
            if dict_payslip_lines.get(list_line['code'], False):
                dict_payslip_lines[
                    list_line['code']]["total"] += list_line["total"]
            else:
                dict_payslip_lines[list_line['code']] = list_line

        return dict_payslip_lines

    def _operation_retention_work_lines(self, retention_line):
        dict_payslip_lines = self._get_lines_payslip_dict()
        result = 0.0
        for rule in retention_line.salary_rule_ids:
            payslip_line = dict_payslip_lines.get(rule.code, {})
            result += payslip_line.get('total', 0.0)
        return result

    def _get_law_parameter(self):
        parameter_retention_id = self.env['ir.config_parameter'].sudo(
        ).get_param('hr_payroll.parameter_retention_id')
        if not parameter_retention_id:
            raise ValidationError(
                _(
                    "You must configure the grade parameters "
                    "to perform the withholding calculations"
                )
            )
        return self.env['hr.payroll.parameter.retention'].browse(
            [int(parameter_retention_id)])

    def _get_amount_about_document_deductions(self, line, retention_employee):
        documents_employee = self.env['hr.employee.document.line'].search(
            [('employee_id', '=', self.employee_id.id)])
        document_amount = 0.0
        for document in documents_employee:
            if document.document_type_id.code == line.document_code:
                amount = self.uvt_validator(line, document, retention_employee)
                retention_employee[f'{line.code.lower()}'] = \
                    amount
                document_amount = amount
        return document_amount, retention_employee

    def uvt_validator(self, line, document, retention_employee):
        amount = document.amount_contributibe
        if line.document_code == "PAD":
            most_recent_low_parameter = self._get_most_recent_law_parameter()
            percentage = line.maximum_percentage\
                if line.maximum_percentage else 100
            percentage = percentage / 100
            amount = self.calc_discount(
                retention_employee["labor_income"],
                percentage)
            if line.uvt_maximum:
                max_amount = line.uvt_maximum * most_recent_low_parameter.uvt
                amount = max_amount if amount > max_amount else amount
        return amount

    def _get_most_recent_law_parameter(self):
        most_recent_low_parameter = self.env['hr.payroll.parameter.retention']\
            .search([], order='year desc', limit=1)
        return most_recent_low_parameter if\
            len(most_recent_low_parameter) > 0 else False

    # OK
    def _get_retention_work(self):
        retention_work = self._get_retention_source_item('1')
        working_revenue = 0.0
        for line in retention_work.line_ids:
            working_revenue += self._operation_retention_work_lines(line)
        return working_revenue

    # OK
    def _get_non_contingent_income(self):
        contingent_income_items = self._get_retention_source_item('2')
        contingent_income = 0.0
        for line in contingent_income_items.line_ids:
            contingent_income += self._operation_retention_work_lines(line)
        return contingent_income

    # Depende de funcionalidad de adjuntar documentos de empleado
    def _get_deductions(self, retention_employee):
        deductions_items = self._get_retention_source_item('3')
        deductions = 0.0
        sum_deductions = 0.0
        for line in deductions_items.line_ids:
            deductions, retention_employee = \
                self._get_amount_about_document_deductions(
                    line,
                    retention_employee
                )
            sum_deductions += deductions
        return sum_deductions, retention_employee

    # OK
    def _additional_calculations_exempt_income(self, line_amount, line,
                                               working_revenue):
        parameter_retention_id = self._get_law_parameter()
        if line.maximum_percentage:
            income_work = working_revenue * (line.maximum_percentage / 100)
            line_amount = (
                income_work - abs(line_amount) if abs(line_amount) >
                income_work else line_amount
            )
            if line.uvt_maximum:
                uvt_amount_line = income_work / parameter_retention_id.uvt
                line_amount = (income_work if uvt_amount_line >
                               line.uvt_maximum else line_amount)

        return line_amount

    def _get_exempt_income(self, working_revenue):
        exempt_income_items = self._get_retention_source_item('4')
        exempt_income = 0.0

        for line in exempt_income_items.line_ids:

            result = self._operation_retention_work_lines(line)
            line_amount = self._additional_calculations_exempt_income(
                result,
                line,
                working_revenue) if result != 0 else result
            exempt_income += abs(line_amount)
        return exempt_income

    def _get_exempt_work_income(self, subtotal_3):
        exempt_work_income_items = self._get_retention_source_item('5')
        exempt_work_income = 0.0
        for line in exempt_work_income_items.line_ids:
            exempt_work_income += round(
                subtotal_3 * (line.maximum_percentage / 100), -3)
        return exempt_work_income

    def _get_extra_calculations(self, subtotal_1, deductions,
                                exempt_income, exempt_work_income,
                                retention_employee):
        parameter_retention_id = self._get_law_parameter()
        deductions_exempt_income = round(
            subtotal_1 * (parameter_retention_id.check_figure / 100), -3)

        retention_employee['ctrl_fgr_ddc_exempt_income'] = \
            deductions_exempt_income
        sum_deductions_exempt_income = abs(
            deductions) + exempt_income + exempt_work_income
        retention_employee['sum_deductions_exempt_income'] = \
            sum_deductions_exempt_income

        resutl_maximum_uvt = round(
            parameter_retention_id.uvt_allowed * parameter_retention_id.uvt,
            -3
        )
        retention_employee['resutl_maximum_uvt'] = \
            resutl_maximum_uvt

        monthly_work_income = (
            subtotal_1 - min(
                deductions_exempt_income,
                sum_deductions_exempt_income,
                resutl_maximum_uvt
            )
        )
        monthly_work_income = self.validate_liquidation_apportionment(
            monthly_work_income)

        retention_employee['monthly_work_income'] = monthly_work_income

        income_taxed_uvt = round(
            monthly_work_income / parameter_retention_id.uvt, 2)
        retention_employee['income_taxed_uvt'] = income_taxed_uvt

        return income_taxed_uvt, retention_employee

    def _calculate_final_withholding(self, subtotal_1, deductions,
                                     exempt_income, exempt_work_income,
                                     retention_employee):
        income_taxed_uvt, retention_employee = self._get_extra_calculations(
            subtotal_1, deductions, exempt_income,
            exempt_work_income, retention_employee)
        uvt_retention_lines = self.env['hr.payroll.uvt.range'].search([])
        parameter_retention_id = self._get_law_parameter()
        retention_source = 0.0
        for line in uvt_retention_lines:
            percentage = f"percent{line.percentage}"
            retention_employee[percentage] = 0
            if ((income_taxed_uvt > line.uvt_amount_subtract
                    and income_taxed_uvt <= line.uvt_quantity
                    and line.percentage)
                    or (line.is_superior_uvt
                        and income_taxed_uvt > line.uvt_quantity)):
                retention_source = round(
                    ((
                        (income_taxed_uvt - line.uvt_amount_subtract) *
                        (line.percentage / 100)
                    ) * parameter_retention_id.uvt) +
                    (line.uvt_amount_add * parameter_retention_id.uvt), -3
                )
                retention_employee[percentage] = retention_source
        return retention_source, retention_employee

    def _get_data_retention_employee(self):
        retention_employee = {
            'name': self.name,
            'employee_id': self.employee_id.id,
            'payslip_id': self.id
        }
        return retention_employee

    def create_retention_employee(self, retention_employee):
        previous_retention_id = self.env[
            'hr.payroll.employee.retention'].search(
                [('employee_id', '=', self.employee_id.id),
                 ('payslip_id', '=', self.id)])
        if previous_retention_id:
            previous_retention_id.unlink()
        self.env['hr.payroll.employee.retention'].create(retention_employee)

    def _get_withholding_tax_calculation(self):
        self.compute_line_ids()
        retention_values = self.get_values_retention()
        retention_employee = self._get_data_retention_employee()
        working_revenue = self._get_retention_work()
        retention_employee['labor_income'] = working_revenue

        contingent_income = self._get_non_contingent_income()
        subtotal_1 = round(working_revenue - abs(contingent_income), -3)

        retention_employee['total_non_constitutive_income'] = \
            round(abs(contingent_income), -2)
        retention_employee['subtotal1'] = subtotal_1

        deductions, retention_employee = \
            self._get_deductions(retention_employee)
        subtotal_2 = subtotal_1 - deductions
        retention_employee['total_deductions'] = deductions
        retention_employee['subtotal2'] = subtotal_2

        exempt_income = self._get_exempt_income(working_revenue)
        retention_employee['total_exempt_income'] = exempt_income
        subtotal_3 = subtotal_2 - exempt_income
        retention_employee['subtotal3'] = subtotal_3

        exempt_work_income = self._get_exempt_work_income(subtotal_3)
        subtotal_4 = subtotal_3 - exempt_work_income
        retention_employee['exempt_labor_income'] = exempt_work_income
        retention_employee['subtotal4'] = subtotal_4

        retention_source, retention_employee = \
            self._calculate_final_withholding(
                subtotal_1, deductions, exempt_income,
                exempt_work_income, retention_employee
            )
        retention_employee['amount'] = retention_source
        retention_employee['salary'] = retention_values.get('BASIC', 0)
        retention_employee['non_salary_bonus'] = \
            retention_values.get('BONUSES', 0)
        retention_employee['bonus'] = retention_values.get('BOND', 0)
        retention_employee['vlnt_cntr_pension_fund_empl'] = \
            retention_values.get('VLN_CONTRIBUTION', 0)
        retention_employee['mandatory_pension_contributions'] = \
            abs(retention_values.get('3020', 0))
        retention_employee['mnd_cntr_pension_salidarity_fund'] = \
            round(abs(retention_values.get('3023', 0)), -3)
        retention_employee['mnd_cntr_to_health'] = \
            abs(retention_values.get('3010', 0))
        retention_employee['vln_cntr_to_mnd_pension_fund'] = \
            abs(retention_values.get('VLN_CNTR_PENSION_FUND', 0))
        retention_employee['oth_inc_not_constituting_inc'] = \
            abs(retention_values.get('OTH_INC_NOT_CONSTITUTING_INC', 0))
        retention_employee['cntr_vlnt_pension_fund'] = \
            retention_values.get('3026', 0)
        retention_employee['cntr_afc_accounts'] = \
            retention_values.get('3031', 0)
        retention_employee['other_exempt_income'] = \
            retention_values.get('OTHER_RENTALS', 0)

        self.create_retention_employee(retention_employee)

        retention_source = self.substract_old_retention(retention_source)
        return retention_source * -1

    def compute_sheet(self):
        result = super(HrPayslip, self).compute_sheet()
        for payslip in self.filtered(
                lambda slip: slip.state not in ['cancel', 'done']):
            retention_source = payslip._get_withholding_tax_calculation()
            if retention_source != 0:
                lines = [
                    (0, 0, line) for line in payslip._get_payslip_lines()
                ]
                payslip.line_ids.unlink()
                payslip.write(
                    {'line_ids': lines, 'compute_date': fields.Date.today()})
        return result
    
    def truncate_decimals(self, value, decimals):
        split_value = str(value).split(".")
        txt = split_value[1][:decimals] if len(split_value) > 1 else '0'
        txt = txt if len(txt) == decimals else str(txt) + ('0' * (decimals - 1)) 
        return int(value), int(txt)
        
    def round_value_dian(self, int_value, decimal_value):
        if decimal_value >= 60:
            int_value += 1
        elif decimal_value >= 50 and decimal_value < 60 and decimal_value % 2 != 0:
            int_value += 1
        return int_value

    def get_values_retention(self):
        lines_retention = dict(
            (line.code, line.salary_rule_ids)
            for line in self.env['hr.payroll.retention.line'].search([])
        )
        lines_retention_values = dict()
        for line in lines_retention:
            values = 0
            for salary_rule in lines_retention[line]:
                for line_id in self.line_ids_compute:
                    if salary_rule == line_id.salary_rule_id:
                        values += line_id.total
                        break
            lines_retention_values[line] = values
        return lines_retention_values

    def calc_discount(self, labor_income, percentage):
        # Validate dependent document
        documents = self.employee_id.documents_employee_ids
        amount = 0
        for document in documents:
            if document.expiration_date\
                    and document.document_type_id.code == "PAD"\
                    and document.expiration_date >= self.date_from\
                    and document.state == "enabled":
                # Assign amount percentage of basic salary discount
                amount = labor_income * percentage
                document.amount_contributibe = amount

        return amount

    def validate_liquidation_apportionment(self, monthly_work_income):
        init_date = self.date_from
        end_date = self.date_to
        delta = end_date - init_date
        count_days = delta.days + 1
        monthly_work_income = self.get_liquidation_values(monthly_work_income)\
            if self.struct_id.type_id.name == "Liquidación" and\
            count_days < 30 else monthly_work_income
        return monthly_work_income

    def get_liquidation_values(self, monthly_work_income):
        days_quantity = 0
        for rule in self.line_ids_compute:
            if rule.code == "BASIC" or rule.code == "26" or rule.code == "280"\
                    or rule.code == "145" or rule.code == "146"\
                    or rule.code == "147" or rule.code == "27"\
                    or rule.code == "25":
                days_quantity += rule.quantity

        holidays_no_enjoyment = self.get_holidays_no_enjoyment()
        days_quantity += holidays_no_enjoyment
        # monthly_work_income = (monthly_work_income/days_quantity)*30
        return monthly_work_income

    def get_holidays_no_enjoyment(self):
        enjoyment_days = 0
        holiday_laps = self.env["hr.payroll.holiday.lapse"].search([
            ("employee_id", "=", self.employee_id.id)])
        for holiday_lap in holiday_laps:
            enjoyment_days += holiday_lap.days_taken
        no_enjoyment_days = self.get_acumulate_holidays_no_enjoyment()
        no_enjoyment_days = no_enjoyment_days - enjoyment_days
        return no_enjoyment_days

    def get_acumulate_holidays_no_enjoyment(self):
        init_date = self.contract_id.date_start
        end_date = self.date_to
        delta = end_date - init_date
        reldelta = relativedelta(end_date, init_date)
        settlement = self.env["settlement.history"].search([
            ('payslip_id', '=', self.id)
        ])
        days = settlement.work_days
        return (days * 15) / 360

    def search_all_payslips(self, include=True):
        date_from = self.get_range_period()
        if include:
            payslips = self.env["hr.payslip"].search([
                ("employee_id", "=", self.employee_id.id),
                ("date_from", ">=", date_from),
                ("id", "<=", self.id)
            ])
        else:
            payslips = self.env["hr.payslip"].search([
                ("employee_id", "=", self.employee_id.id),
                ("date_from", ">=", date_from),
                ("id", "<", self.id)
            ])
        return payslips

    def get_range_period(self):
        date_from = self.date_from
        date_from = date(date_from.year, date_from.month, 1)
        return date_from

    def compute_line_ids(self):
        payslips = self.search_all_payslips()
        local_line_ids = self.env['hr.payslip.line']
        for payslip in payslips:
            for line_id in payslip.line_ids:
                local_line_ids += line_id
        self.line_ids_compute = local_line_ids

    def substract_old_retention(self, retention_source):
        payslips = self.search_all_payslips(False)
        old_retentions = 0

        if payslips:
            for payslip in payslips:
                for line in payslip.line_ids:
                    old_retentions += line.total if line['code'] == '3008'\
                        else 0
        retention_source += old_retentions
        return retention_source
