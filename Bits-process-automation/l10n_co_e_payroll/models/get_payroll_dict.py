# -*- coding: utf-8 -*-
from pytz import timezone

class GetPayrollDict():

    @classmethod
    def generate_dict_api_service(cls, provider, req_tp_lines, localdict=None):

        def _generate_lines(localdict, line_ids):
            res = []
            payslip = localdict['payslip']

            new_check = []
            holiday_history_check = []
            category_checked = []
            parents_checked = []

            # CHECK REQUIRED LINES
            for req_tp_line in req_tp_lines:
                if req_tp_line not in parents_checked:
                    res, parents_checked = (
                        _process_line_information(
                            localdict, res, req_tp_line, parents_checked
                            )
                        )

            for line in payslip.line_ids:
                localdict['payslip_line'] = line
                localdict['payroll_new'] = False
                localdict['holiday_history'] = False
                salary_rule = line.salary_rule_id
                if salary_rule and salary_rule.tech_provider_line_id:
                    tp_line = salary_rule.tech_provider_line_id
                    rule_category = salary_rule.l10n_type_rule
                else:
                    tp_line = False
                if tp_line:

                    # KEEP OLD VALIDATIONS
                    act_field = tp_line.act_field_id
                    if act_field and not (
                        act_field._satisfy_condition(localdict)
                    ):
                        continue
                    if act_field:
                        act_field.validate_required_field(localdict)

                    if line.payroll_news_id:
                        for payroll_new in line.payroll_news_id:
                            pn_type = payroll_new.salary_rule_id.l10n_type_rule
                            if (
                                payroll_new in new_check and
                                rule_category in category_checked
                            ):
                                continue
                            if payroll_new.holiday_history_id:
                                hday_history = (
                                    payroll_new.holiday_history_id
                                )
                                if (
                                    hday_history in holiday_history_check and
                                    rule_category in category_checked and
                                    (
                                        payroll_new in new_check or
                                        pn_type == 'enjoyment_rule'
                                    )
                                ):
                                    continue
                                localdict['holiday_history'] = hday_history
                                holiday_history_check.append(hday_history)
                            localdict['payroll_new'] = payroll_new

                            res, parents_checked = (
                                _process_line_information(
                                    localdict,
                                    res,
                                    tp_line,
                                    parents_checked
                                )
                            )
                            new_check.append(payroll_new)
                            category_checked.append(rule_category)
                    else:
                        res, parents_checked = (
                            _process_line_information(
                                localdict,
                                res,
                                tp_line,
                                parents_checked
                            )
                        )
            new_res = []
            empty_list = ['', ' ', '0%', '0.0', '0.0000', '0', 0, False]
            for row in res:
                if 'sequence' in row:
                    information = False
                    if row['lines']:
                        for row_dict_line in row['lines']:
                            if (
                                row_dict_line['value'] not in empty_list or 
                                row['cardinality'] in ['1_1', '1_n']
                            ):
                                information = True
                        if information:
                            row['lines'] = (
                                sorted(row['lines'], key=lambda k: k['code'])
                            )
                            new_res.append(row)
            res = sorted(new_res, key=lambda k: k['sequence'])
            return res

        def _generate_children(localdict, children_ids):
            lines = []
            for field_line in children_ids:
                rule = field_line.act_field_id
                if rule and not rule._satisfy_condition(localdict):
                    continue
                rule.validate_required_field(localdict)
                if field_line.children_ids:
                    row = dict()
                    row['head'] = field_line.code
                    row['sequence'] = field_line.sequence
                    row['cardinality'] = field_line.cardinality
                    row['lines'] = []
                    if rule and rule._compute_rule(localdict):
                        head = rule._compute_rule(localdict)
                        if not isinstance(head, list):
                            row['lines'] = _generate_children(
                                localdict, field_line.children_ids)
                            lines.append(row)
                        else:
                            for head_line in head:
                                localdict['record_1'] = head_line
                                lines.append({
                                    'head': field_line.code,
                                    'sequence': field_line.sequence,
                                    'cardinality': field_line.cardinality,
                                    'lines': _generate_children(
                                        localdict, field_line.children_ids)
                                })
                        continue
                value = ''
                rule = field_line.act_field_id
                compute_rule = rule._compute_rule(localdict)
                if compute_rule:
                    value = compute_rule
                elif not isinstance(compute_rule, bool):
                    value = compute_rule

                line_row = {
                    'label': field_line.name,
                    'code': field_line.code,
                    'value': value,
                    'type': type(value),
                }
                lines.append(line_row)
            return lines

        def _process_line_information(localdict, res, tp_line, par_checked):
            row = dict()
            if tp_line.parent_id and not (
                (tp_line.parent_id in par_checked) or
                (tp_line.parent_id.cardinality in ['0_n', '1_n'])
            ):
                row['head'] = tp_line.parent_id.code
                row['sequence'] = tp_line.parent_id.sequence
                row['cardinality'] = tp_line.parent_id.cardinality
                row['lines'] = []

                act_field = tp_line.parent_id.act_field_id
                if act_field and act_field._compute_rule(localdict):
                    headers = act_field._compute_rule(localdict)
                    for head in headers:
                        localdict['record'] = head
                        row['lines'].append(_generate_children(
                            localdict, tp_line.parent_id.children_ids))
                else:
                    row['lines'] = _generate_children(
                        localdict, tp_line.parent_id.children_ids)
                par_checked.append(tp_line.parent_id)
            elif not tp_line.parent_id and (
                (tp_line not in par_checked) or
                (tp_line.cardinality in ['0_n', '1_n'])
            ):
                row['head'] = tp_line.code
                row['sequence'] = tp_line.sequence
                row['cardinality'] = tp_line.cardinality
                row['lines'] = []
                if tp_line.act_field_id and (
                    tp_line.act_field_id._compute_rule(localdict)
                ):
                    headers = tp_line.act_field_id._compute_rule(localdict)
                    if isinstance(headers, int) or isinstance(headers, str):
                        row['lines'].append(_generate_children(
                                localdict, [tp_line]))
                    else:
                        for head in headers:
                            localdict['record'] = head
                            row['lines'].append(_generate_children(
                                localdict, tp_line.children_ids))
                else:
                    row['lines'] = _generate_children(
                        localdict, tp_line.children_ids)
                par_checked.append(tp_line)
            res.append(row)

            return res, par_checked

        res = _generate_lines(localdict, provider.line_ids)
        return res
