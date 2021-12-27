# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from contextlib import contextmanager
import locale
import logging
from odoo.http import request
from datetime import datetime
from odoo import models, fields, api, _
from odoo.tools.misc import formatLang, format_date, get_lang
from werkzeug.urls import url_encode
import functools
import operator

_logger = logging.getLogger(__name__)


class payroll_holidays_report(models.Model):
    _name = 'hr.payslip'
    _inherit = ['hr.payslip']

    period_start_date = fields.Char(
        compute="_compute_period_start_date")
    period_finish_date = fields.Char(
        compute="_compute_period_end_date")

    start_holidays = fields.Char(
        compute="_compute_enjoyment_start_date")
    end_holidays = fields.Char(
        compute="_compute_enjoyment_end_date")

    date_now = fields.Char(
        compute="_compute_date_now")

    def _compute_date_now(self):
        date = datetime.now()
        self.date_now = self.date_format(date)

    def _compute_period_start_date(self):
        for record in self:
            starting_dates =\
                [novelty.holiday_history_id.holiday_lapse.begin_date
                    for novelty in record.line_ids.payroll_news_id]
            date = min(starting_dates) if starting_dates else False

            record.period_start_date = self.date_format(date)

    def _compute_period_end_date(self):
        for record in self:
            end_dates =\
                [novelty.holiday_history_id.holiday_lapse.end_date
                    for novelty in record.line_ids.payroll_news_id]
            date = max(end_dates) if end_dates else False

            record.period_finish_date = self.date_format(date)

    def _compute_enjoyment_start_date(self):
        for record in self:
            starting_dates =\
                [novelty.holiday_history_id.enjoyment_start_date
                    for novelty in record.line_ids.payroll_news_id]
            date = min(starting_dates) if starting_dates else False

            record.start_holidays = self.date_format(date)

    def _compute_enjoyment_end_date(self):
        for record in self:
            end_dates =\
                [novelty.holiday_history_id.enjoyment_end_date
                    for novelty in record.line_ids.payroll_news_id]
            date = max(end_dates) if end_dates else False

            record.end_holidays = self.date_format(date)

    def date_format(self, date):
        self.ensure_one()
        if date is not False:
            dict_month = {
                '1': "Enero",
                '2': "Febrero",
                '3': "Marzo",
                '4': "Abril",
                '5': "Mayo",
                '6': "Junio",
                '7': "Julio",
                '8': "Agosto",
                '9': "Septiembre",
                '10': "Octubre",
                '11': "Noviembre",
                '12': "Diciembre",
            }
            day = date.day
            month = (
                dict_month.get(
                    f"{date.month}", 0))
            year = date.year
            complete_date = "{} de {} de {}".format(
                                                    str(day),
                                                    str(month),
                                                    str(year))
            return complete_date
