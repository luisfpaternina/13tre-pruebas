from os import symlink
from pandas.core.frame import DataFrame
from pandas.core.reshape.pivot import pivot_table
from odoo import api, fields, models, _
from odoo.tools.misc import xlwt
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError
import base64
import pandas as pd
import numpy as np
import xlsxwriter
import logging
import json
from operator import itemgetter
from itertools import count, groupby, permutations
from io import BytesIO
_logger = logging.getLogger(__name__)


class WizardAccountExogenusPrintXls(models.TransientModel):
    _name = 'wizard.account.exogenus.print.xls'

    date_from = fields.Date(string='Start Date', required=True)
    date_to = fields.Date(string='End Date', required=True)
    format_id = fields.Many2one('account.format.exogenus', string="Format")
    format_type = fields.Selection(
        related="format_id.format_type",
        string="Format type")
    company_id = fields.Many2one('res.company',
                                 default=lambda self: self.env.company)
    partner_id = fields.Many2one('res.partner', string="Third")

    @api.constrains('date_from')
    def _check_exist_record_in_lines(self):
        if self.date_from > self.date_to:
            raise ValidationError(_(
                'The start date cannot be greater than the end date'))

    def _init_buffer(self, output):
        self.generate_xlsx(output)
        return output

    def action_generate_xlsx_report(self):
        return {
            'type': 'ir.actions.act_url',
            'url': 'reports/format/{}/{}/{}'.format(
                self._name, 'xlsx', self.id),
            'target': 'new'
        }

    def file_name(self, file_format='xlsx'):
        file_name = "%s.%s" % (
            (self.format_id.name).replace(' ', '_'), file_format)
        return file_name

    def document_print(self):
        output = BytesIO()
        output = self._init_buffer(output)
        output.seek(0)
        return output.read()

    """def generate_xlsx(self, output):
        workbook = xlsxwriter.Workbook(output)
        ws = workbook.add_worksheet(self.format_id.name)
        col = 0
        keys = {}
        test = {}
        aml_fields = []
        test_list = []
        colunms = []
        row = 2
        title1 = workbook.add_format({
            'font_size': 14,
            'align': 'center',
            'text_wrap': True,
            'bold': True,
            'border': 1})
        title2 = workbook.add_format({
            'font_size': 14,
            'align': 'left',
            'text_wrap': True,
            'bold': True})
        number_format = workbook.add_format({
            'align': 'right',
            'num_format': '#,##0.00'
            })
        ws.merge_range("A1:C1", self.format_id.description, title2)
        for title in self.format_id.account_column_ids.\
                sorted(lambda r: r.sequence):
            colunms.append(title.account_column_id.name)
            ws.set_column(col, col, len(title.account_column_id.name) + 5)
            ws.write(row, col, title.account_column_id.name, title1)
            keys.setdefault(
                title.account_column_id, [col, \
                    title.account_column_id.bool_delete])
            col += 1
        # have concept but not lesser amount
        if self.format_id.bool_concept and not self.\
                format_id.bool_lesser_amount:
            query = self._query_values_group_partner_concept_exogenus()
            result_aml = query if query else []
        # not concept but have lesser amount
        # (group partner,account and lesser amount)
        elif not self.format_id.bool_concept and self.\
                format_id.bool_lesser_amount:
            query = self._query_values_group_partner_and_amount()
            result_aml = query if query else []
        # not concept and lesser amount (group partner and account)
        elif not self.format_id.bool_concept and not self.\
                format_id.bool_lesser_amount:
            if self.format_id.bool_amount:
                query = self._query_values_art_4_6()
            elif self.format_id.partner_report:
                query = self._query_shareholders()
            else:
                query = self._query_values_group_partner_and_account()
            result_aml = query if query else []
        # have concept and lesser amount
        else:
            query = self._query_values_group_concept_and_amount()
            result_aml = query if query else []
        row += 1
        for key, value in keys.items():
            if value[1] == True:
                aml_fields.append('{}'.format(key.id))
            final_data = []
            for line in result_aml:
                final_data.append(key.execute_code(line,self) or None)
            test['{}'.format(key.id)] = final_data
        df = pd.DataFrame(test)
        aml_fields = set(aml_fields)
        aml_fields = list(aml_fields)
        filtered_df = df[aml_fields].isnull()
        filtered_df = filtered_df.sum(axis=1)
        filtered_df = dict(filtered_df)
        for item, val in filtered_df.items():
            if val == len(aml_fields):
                test_list.append(item)
        df_clean = df.drop(test_list,axis=0)
        workbook.close()
        return output"""

    def generate_xlsx(self, output):
        col = 0
        keys = {}
        test = {}
        aml_fields = []
        test_list = []
        colunms = []
        row = 2
        for title in self.format_id.account_column_ids.\
                sorted(lambda r: r.sequence):
            colunms.append(title.account_column_id.name)
            keys.setdefault(
                title.account_column_id,
                [col, title.account_column_id.bool_delete])
            col += 1
        # have concept but not lesser amount
        if self.format_id.bool_concept and not self.\
                format_id.bool_lesser_amount:
            query = self._query_values_group_partner_concept_exogenus()
            result_aml = query if query else []
        # not concept but have lesser amount
        # (group partner,account and lesser amount)
        elif not self.format_id.bool_concept and self.\
                format_id.bool_lesser_amount:
            query = self._query_values_group_partner_and_amount()
            result_aml = query if query else []
        # not concept and lesser amount (group partner and account)
        elif not self.format_id.bool_concept and not self.\
                format_id.bool_lesser_amount:
            if self.format_id.bool_amount:
                query = self._query_values_art_4_6()
            elif self.format_id.partner_report:
                query = self._query_shareholders()
            else:
                query = self._query_values_group_partner_and_account()
            result_aml = query if query else []
        # have concept and lesser amount
        else:
            query = self._query_values_group_concept_and_amount()
            result_aml = query if query else []
        row += 1
        for key, value in keys.items():
            if value[1]:
                aml_fields.append('{}'.format(key.id))
            final_data = []
            for line in result_aml:
                final_data.append(key.execute_code(line, self) or None)
            test['{}'.format(key.id)] = final_data
        df = pd.DataFrame(test)
        print(df)
        aml_fields = set(aml_fields)
        print(aml_fields)
        aml_fields = list(aml_fields)
        filtered_df = df[aml_fields].isnull()
        filtered_df = filtered_df.sum(axis=1)
        filtered_df = dict(filtered_df)
        for item, val in filtered_df.items():
            test_list += [item] if val == len(aml_fields) else []
        df_clean = df.drop(test_list, axis=0)
        print(df_clean)
        book_name = '{}.xlsx'.format(self.format_id.name)
        sheet_name = '{}'.format(self.format_id.name)
        writer = pd.ExcelWriter(book_name, engine='xlsxwriter')
        writer.book.filename = output
        df_clean.to_excel(
            writer,
            sheet_name=sheet_name,
            startrow=3,
            startcol=0,
            header=False,
            index=False)
        workbook = writer.book
        worksheet = writer.sheets[sheet_name]
        title1 = workbook.add_format({
            'font_size': 14,
            'align': 'center',
            'text_wrap': True,
            'bold': True,
            'border': 1})
        title2 = workbook.add_format({
            'font_size': 14,
            'align': 'left',
            'text_wrap': True,
            'bold': True})
        number_format = workbook.add_format({
            'align': 'right',
            'num_format': '#,##0.00'
            })
        worksheet.merge_range("A1:C1", self.format_id.description, title2)
        (max_row, max_col) = df.shape
        column_settings = [{'header': column} for column in df.columns]
        worksheet.add_table(
            2,
            0,
            max_row, max_col - 1,
            {'columns': column_settings})
        worksheet.set_column(0, max_col - 1, 12)
        col = 0
        row = 2
        for title in self.format_id.account_column_ids.\
                sorted(lambda r: r.sequence):
            worksheet.set_column(
                col,
                col,
                len(title.account_column_id.name) + 5)
            worksheet.write(row, col, title.account_column_id.name, title1)
            col += 1
        writer.save()
        return output

    def _drop_temporary(self):
        return self.env.cr.execute("DROP TABLE temp_account_exogenus_partner")

    def _query_str(self):
        query_str = """select * from temp_account_exogenus_partner"""
        return query_str

    def _case_without_concept(self):
        select = (
            """WITH
                m1 AS
                (
                select aml.partner_id,
                rp.document_type,rp.vat,rp.first_name,
                rp.first_surname,rp.second_surname,rp.second_name,
                rp.street,rp.phone,rp.email,rp.name,rp.state_code,
                rp.country_code,rpt.l10n_co_divipola,aml.account_id,
                (case WHEN COALESCE(aa.lower_amount,0) > 500000
                THEN 1 ELSE 0 END) AS cuantia_menor
                from account_move_line aml
                left join account_account aa on (aml.account_id = aa.id)
                left join res_partner rp on (aml.partner_id = rp.id)
                left join res_country_town rpt on (rpt.id = rp.town_id)
                where aa.lower_amount > 500000
                and aml.partner_id is not NULL
                and aml.id in %(partner_ids)s
                and aml.partner_id != %(partner)s
                group by aml.partner_id,aml.account_id,
                rp.document_type,rp.vat,rp.first_name,
                rp.first_surname,rp.second_surname,rp.second_name,
                rp.street,rp.phone,rp.email,rp.name,rp.state_code,
                rp.country_code,rpt.l10n_co_divipola,
                (case WHEN (COALESCE(aa.lower_amount,0) > 500000)
                THEN 1 ELSE 0 end)
                ),
                m2 AS
                (
                select aml.partner_id,rp.document_type,rp.vat,rp.first_name,
                rp.first_surname,rp.second_surname,rp.second_name,
                rp.street,rp.phone,rp.email,rp.name,rp.state_code,
                rp.country_code,rpt.l10n_co_divipola,aml.account_id,
                (case WHEN (COALESCE(aa.lower_amount,0) > 500000)
                THEN 1 ELSE 0 END) AS cuantia_menor,
                ROW_number () over( partition BY aml.partner_id) AS contar
                from account_move_line aml
                left join account_account aa on (aml.account_id = aa.id)
                left join res_partner rp on (aml.partner_id = rp.id)
                left join res_country_town rpt on (rpt.id = rp.town_id)
                where partner_id is not NULL
                AND COALESCE(aa.lower_amount,0) <= 500000
                and aml.id in %(partner_ids)s and aml.partner_id != %(partner)s
                group by aml.partner_id,aml.account_id,rp.document_type,rp.vat,
                rp.first_name,rp.first_surname,rp.second_surname,rp.second_name,
                rp.street,rp.phone,rp.email,rp.name,rp.state_code,
                rp.country_code,rpt.l10n_co_divipola,
                (case WHEN (COALESCE(aa.lower_amount,0) > 500000)
                THEN 1 ELSE 0 end)
                ),
                m3 AS
                (
                SELECT m2.partner_id,m2.document_type,m2.vat,m2.first_name,
                m2.first_surname,m2.second_surname,m2.second_name,
                m2.street,m2.phone,m2.email,m2.name,m2.state_code,
                m2.country_code,m2.l10n_co_divipola,
                m2.account_id,m2.cuantia_menor
                FROM m2
                WHERE m2.contar=1
                ),
                m4 AS
                (
                SELECT m1.partner_id,m1.document_type,m1.vat,m1.first_name,
                m1.first_surname,m1.second_surname,m1.second_name,
                m1.street,m1.phone,m1.email,m1.name,m1.state_code,
                m1.country_code,m1.l10n_co_divipola,
                m1.account_id,m1.cuantia_menor FROM m1
                UNION
                SELECT m3.partner_id,m3.document_type,m3.vat,m3.first_name,
                m3.first_surname,m3.second_surname,m3.second_name,
                m3.street,m3.phone,m3.email,m3.name,m3.state_code,
                m3.country_code,m3.l10n_co_divipola,
                m3.account_id,m3.cuantia_menor FROM m3
                )select * into TEMPORARY
                temp_account_exogenus_partner from m4;
            """
            )
        return select

    def _query_values_group_partner_and_amount(self):
        move_line_objs = self._get_values()
        params = {
                'partner': self.partner_id.id if self.partner_id else 0,
                'partner_ids': tuple(move_line_objs.ids)
            }
        sql_with = self._case_without_concept()
        query_str = self._query_str()
        self.flush()
        self.env.cr.execute(sql_with + query_str, params)
        partners = self.env.cr.dictfetchall()
        self._drop_temporary()
        return partners

    def _query_values_group_partner_and_account(self):
        move_line_objs = self._get_values()
        params = {
                'partner': self.partner_id.id if self.partner_id else 0,
                'partner_ids': tuple(move_line_objs.ids)
            }
        select = """with
                    rpt as
                    (
                    select id,l10n_co_divipola from
                    res_country_town
                    ),
                    m1 as
                    (
                    select aml.partner_id,
                    rp.document_type,rp.vat,rp.first_name,
                    rp.first_surname,rp.second_surname,rp.second_name,
                    rp.name,aml.account_id,rpt.l10n_co_divipola,
                    rp.street,rp.phone,rp.email,rp.state_code,
                    rp.country_code
                    from rpt,account_move_line aml
                    left join res_partner rp
                    on (rp.id = aml.partner_id)
                    where aml.partner_id is not null
                    and aml.partner_id != %(partner)s
                    and aml.id in %(partner_ids)s
                    and rpt.id = rp.town_id
                    group by aml.partner_id,aml.account_id,rp.document_type,
                    rp.vat,rp.first_name,rp.first_surname,rp.second_surname,
                    rp.second_name,rp.name,
                    rpt.l10n_co_divipola,
                    rp.street,rp.phone,rp.email,rp.state_code,
                    rp.country_code
                    )select * into TEMPORARY
                    temp_account_exogenus_partner from m1;
                    """
        query_str = self._query_str()
        self.flush()
        self.env.cr.execute(select + query_str, params)
        partners = self.env.cr.dictfetchall()
        self._drop_temporary()
        return partners

    def _query_values_group_partner_concept_exogenus(self):
        move_line_objs = self._get_values()
        params = {
            'partner': self.partner_id.id if self.partner_id else 0,
            'partner_ids': tuple(move_line_objs.ids),
            'format_id': self.format_id.id
        }
        select = """with
                    m1 as
                    (
                    select ax.concept_exogenus_id,
                    aml.partner_id,rp.document_type,
                    rp.vat,rp.first_name,
                    rp.first_surname,rp.second_surname,
                    rp.second_name,rpt.l10n_co_divipola,
                    rp.street,rp.phone,rp.email,rp.name,
                    rp.state_code,rp.country_code
                    from account_move_line aml
                    join account_concept_exogenus_line ax
                    on (ax.account_id = aml.account_id)
                    left join res_partner rp
                    on (rp.id = aml.partner_id)
                    left join res_country_town rpt
                    on (rpt.id = rp.town_id)
                    join account_concept_exogenus acx
                    on (ax.concept_exogenus_id = acx.id)
                    where aml.partner_id is not null
                    and aml.debit > ax.lesser_amount
                    and aml.id in %(partner_ids)s and
                    aml.partner_id != %(partner)s
                    and acx.format_exogenus_id = %(format_id)s
                    group by ax.concept_exogenus_id,
                    aml.partner_id,rp.document_type,rp.vat,
                    rp.first_name,rp.first_surname,
                    rp.second_surname,rp.second_name,rp.name,
                    rpt.l10n_co_divipola,
                    rp.street,rp.phone,rp.email,
                    rp.state_code,rp.country_code
                    )select * into TEMPORARY
                    temp_account_exogenus_partner from m1;
                """
        query_str = self._query_str()
        self.env.cr.execute(select + query_str, params)
        partners = self.env.cr.dictfetchall()
        self._drop_temporary()
        return partners

    def _case_with_concept(self):
        select = (
            """with
                rp AS
                (
                select rp.id,rp.document_type,rp.vat,rp.first_name,
                rp.first_surname,rp.second_surname,rp.second_name,
                rp.street,rp.phone,rp.email,rp.name,rp.state_code,
                rp.country_code,rpt.l10n_co_divipola
                from res_partner
                rp left join res_country_town rpt on
                (rpt.id = rp.town_id)
                ),
                m1 as
                (
                select ax.concept_exogenus_id,rp.document_type,rp.vat,
                rp.first_name,rp.first_surname,rp.second_surname,
                rp.second_name,rp.street,rp.phone,rp.email,rp.name,rp.state_code,
                rp.country_code,rp.l10n_co_divipola,aml.partner_id,ax.lesser_amount,
                aml.debit,
                (case WHEN (aml.debit > ax.lesser_amount) THEN 1 ELSE 0 END)
                as valida
                from rp,account_move_line aml
                join account_concept_exogenus_line ax
                on (ax.account_id = aml.account_id)
                join account_concept_exogenus acx
                on (ax.concept_exogenus_id = acx.id)
                where aml.partner_id is not null
                and aml.debit > ax.lesser_amount
                and aml.id in %(partner_ids)s and aml.partner_id != %(partner)s
                and aml.partner_id = rp.id
                and acx.format_exogenus_id = %(format_id)s
                group by ax.concept_exogenus_id,rp.document_type,rp.vat,
                rp.first_name,rp.first_surname,rp.second_surname,
                rp.second_name,rp.street,rp.phone,rp.email,rp.name,
                rp.state_code,rp.country_code,rp.l10n_co_divipola,aml.partner_id,
                ax.lesser_amount,aml.debit,valida
                ),
                m2 as
                (
                select ax.concept_exogenus_id,rp.document_type,rp.vat,
                rp.first_name,rp.first_surname,rp.second_surname,
                rp.second_name,rp.street,rp.phone,rp.email,rp.name,
                rp.state_code,rp.country_code,rp.l10n_co_divipola,
                aml.partner_id,ax.lesser_amount,aml.debit,
                (case WHEN (aml.debit > ax.lesser_amount) THEN 1 ELSE 0 END)
                as valida,
                ROW_number () over( partition BY ax.concept_exogenus_id)
                AS contar
                from rp,account_move_line aml
                join account_concept_exogenus_line ax
                on (ax.account_id = aml.account_id)
                join account_concept_exogenus acx
                on (ax.concept_exogenus_id = acx.id)
                where aml.partner_id is not null
                and aml.debit <= ax.lesser_amount
                and aml.id in %(partner_ids)s and aml.partner_id != %(partner)s
                and aml.partner_id = rp.id
                and acx.format_exogenus_id = %(format_id)s
                group by ax.concept_exogenus_id,rp.document_type,rp.vat,
                rp.first_name,rp.first_surname,rp.second_surname,
                rp.second_name,rp.street,rp.phone,rp.email,rp.name,
                rp.state_code,rp.country_code,rp.l10n_co_divipola,
                aml.partner_id,ax.lesser_amount,aml.debit,valida
                ),
                m3 as
                (
                select m2.concept_exogenus_id,m2.document_type,m2.vat,
                m2.first_name,m2.first_surname,m2.second_surname,
                m2.second_name,m2.street,m2.phone,m2.email,m2.name,
                m2.state_code,m2.country_code,m2.l10n_co_divipola,
                m2.partner_id,m2.lesser_amount,m2.debit,m2.contar
                from m2
                where m2.contar = 1
                ),
                m4 AS
                (
                select m1.concept_exogenus_id,m1.document_type,m1.vat,
                m1.first_name,m1.first_surname,m1.second_surname,
                m1.second_name,m1.street,m1.phone,m1.email,m1.name,
                m1.state_code,m1.country_code,m1.l10n_co_divipola,
                m1.partner_id,m1.lesser_amount,m1.debit,
                (case WHEN (m1.debit > m1.lesser_amount) THEN 1 ELSE 0 END)
                as valida
                from m1
                UNION
                select m3.concept_exogenus_id,m3.document_type,m3.vat,
                m3.first_name,m3.first_surname,m3.second_surname,
                m3.second_name,m3.street,m3.phone,m3.email,m3.name,
                m3.state_code,m3.country_code,m3.l10n_co_divipola,
                m3.partner_id,m3.lesser_amount,m3.debit,
                (case WHEN (m3.debit > m3.lesser_amount) THEN 1 ELSE 0 END)
                as valida
                from m3
                ),
                m5 as
                (
                SELECT m4.concept_exogenus_id,m4.partner_id,valida,
                m4.lesser_amount,sum(m4.debit) cuantia,m4.document_type,
                m4.vat,m4.first_name,m4.first_surname,m4.second_surname,
                m4.second_name,m4.street,m4.phone,m4.email,m4.name,
                m4.state_code,m4.country_code,m4.l10n_co_divipola
                FROM m4
                GROUP BY m4.concept_exogenus_id,m4.partner_id,
                m4.lesser_amount,m4.document_type,m4.vat,m4.first_name,
                m4.first_surname,m4.second_surname,m4.second_name,
                m4.street,m4.phone,m4.email,m4.name,m4.state_code,
                m4.country_code,m4.l10n_co_divipola,valida
                )select * into TEMPORARY
                temp_account_exogenus_partner from m5;
            """
            )
        return select

    def _query_values_group_concept_and_amount(self):
        partner_obj = 0
        if self.format_id.name == 'Formato 1001' or not self.partner_id:
            partner_obj = 0
        else:
            partner_obj = self.partner_id.id
        move_line_objs = self._get_values()
        params = {
                'partner': partner_obj,
                'partner_ids': tuple(move_line_objs.ids),
                'format_id': self.format_id.id
            }
        sql_with = self._case_with_concept()
        query_str = self._query_str()
        self.flush()
        self.env.cr.execute(sql_with + query_str, params)
        partners = self.env.cr.dictfetchall()
        self._drop_temporary()
        return partners

    def _with_art_4_6(self):
        select = (
            """with
                rp as
                (
                select rp.id,rp.document_type,rp.vat,rp.first_name,
                rp.first_surname,rp.second_surname,rp.second_name,
                rp.street,rp.phone,rp.email,rp.name,rp.state_code,
                rp.country_code,rpt.l10n_co_divipola
                from res_partner
                rp left join res_country_town rpt on
                (rpt.id = rp.town_id)
                ),
                tar as
                (
                select id,abs(amount) as tarifa from account_tax
                ),
                m2m as
                (
                select tar.tarifa, amlt.account_move_line_id
                from tar, account_move_line_account_tax_rel amlt
                where tar.id = amlt.account_tax_id
                ),
                m1 as
                (
                select aml.partner_id,
                rp.document_type,rp.vat,rp.first_name,
                rp.first_surname,rp.second_surname,rp.second_name,
                rp.street,rp.phone,rp.email,rp.name,aml.account_id,
                rp.state_code,rp.country_code,rp.l10n_co_divipola
                ,m2m.tarifa,to_char(aml.date,'YYYY') as date
                from rp,m2m,account_move_line aml
                where rp.id = aml.partner_id
                and aml.partner_id is not null
                and m2m.account_move_line_id = aml.id
                and aml.partner_id != %(partner)s
                and aml.id in %(partner_ids)s
                group by aml.partner_id,aml.account_id,rp.document_type,
                rp.vat,rp.first_name,rp.first_surname,rp.second_surname,
                rp.second_name,rp.name,rp.street,rp.phone,rp.email,
                rp.state_code,rp.country_code,rp.l10n_co_divipola
                ,m2m.tarifa,date
                ) select * into TEMPORARY
                temp_account_exogenus_partner from m1;
            """
            )
        return select

    def _query_values_art_4_6(self):
        move_line_objs = self._get_values()
        params = {
                'partner': self.partner_id.id if self.partner_id else 0,
                'partner_ids': tuple(move_line_objs.ids)
            }
        sql_with = self._with_art_4_6()
        query_str = self._query_str()
        self.flush()
        self.env.cr.execute(sql_with + query_str, params)
        partners = self.env.cr.dictfetchall()
        self._drop_temporary()
        return partners

    def _query_shareholders(self):
        date = str(self.date_to)
        date = int(date[:4])
        params = {
                'date': date
            }
        sql_with = """
                with
                rp AS
                (
                select rp.id,rp.document_type,rp.vat,rp.first_name,
                rp.first_surname,rp.second_surname,rp.second_name,
                rp.street,rp.name,rp.state_code,
                rp.country_code,rpt.l10n_co_divipola
                from res_partner
                rp left join res_country_town rpt on
                (rpt.id = rp.town_id)
                ),
                m1 as
                (
                select asco.year,rp.document_type,rp.vat,rp.first_name,
                rp.first_surname,rp.second_surname,rp.second_name,
                rp.street,rp.name,rp.state_code,rp.country_code,
                rp.l10n_co_divipola,ascl.partner_id,
                ascl.number_shares,ascl.percentage_share,
                ascl.shareholder_contribution
                from rp,account_shareholders_company_line ascl
                left join account_shareholders_company asco
                on (ascl.account_shareholders_company_id = asco.id)
                where rp.id = ascl.partner_id
                and asco.year = %(date)s
                )select * into TEMPORARY
                temp_account_exogenus_partner from m1;
        """
        query_str = self._query_str()
        self.flush()
        self.env.cr.execute(sql_with + query_str, params)
        partners = self.env.cr.dictfetchall()
        self._drop_temporary()
        return partners

    def _get_values(self):
        obj = self.env['account.move.line']
        move_lines = obj.search(self._get_domain())
        return move_lines

    def _get_domain(self):
        domain = [
            ('parent_state', '=', 'posted'),
            ('company_id', '=', self.env.company.id)
        ]
        if self.date_from:
            domain.append(('date', '>=', self.date_from))
        if self.date_to:
            domain.append(('date', '<=', self.date_to))
        if self.format_id.bool_concept:
            concepts = self.env['account.concept.exogenus'].search(
                [('format_exogenus_id', '=', self.format_id.id)])
            acc_concepts = concepts.\
                mapped('concept_exogenus_line_ids.account_id')
            domain += acc_concepts and [(
                'account_id', 'in', acc_concepts.ids)] or []
        return domain
