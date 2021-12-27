# -*- coding: utf-8 -*-


class GettersDict():

    @classmethod
    def generate_dict_api_service(cls, provider, localdict=None):

        def _generate_lines(localdict, line_ids):
            res = []
            for line in line_ids:
                if line.act_field_id and not line.act_field_id\
                   ._satisfy_condition(localdict):
                    continue
                if line.act_field_id:
                    line.act_field_id.validate_required_field(localdict)
                row = dict()
                row['head'] = line.code
                row['lines'] = []
                if line.act_field_id \
                   and line.act_field_id._compute_rule(localdict):
                    headers = line.act_field_id._compute_rule(localdict)
                    for head in headers:
                        localdict['record'] = head
                        row['lines'].append(_generate_children(
                            localdict, line.children_ids))
                else:
                    row['lines'] = _generate_children(
                        localdict, line.children_ids)
                res.append(row)
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
        res = _generate_lines(localdict, provider.line_ids)
        return res
