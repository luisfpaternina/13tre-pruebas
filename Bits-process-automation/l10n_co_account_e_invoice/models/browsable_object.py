# -*- coding: utf-8 -*-

from odoo.tools import formatLang
import pytz
from odoo import fields


class BrowsableObject(object):
    def __init__(self, partner_id, dict, env):
        self.partner_id = partner_id
        self.dict = dict
        self.env = env

    def __getattr__(self, attr):
        return attr in self.dict and self.dict.__getitem__(attr) or 0.0


class Invoive(BrowsableObject):

    def _get_ei_invoice_datetime_time(self, _time, _format="%H:%M:%S"):
        _time = pytz.utc.localize(_time)
        bogota_tz = pytz.timezone('America/Bogota')
        _time = _time.astimezone(bogota_tz)
        return _time.strftime(_format)

    def _get_dict_by_group(self, retention=None):
        return self.dict._get_dict_by_group(retention)

    def _get_total_type_retention(self):
        return self.dict._get_total_type_retention()

    def _get_total_type_transferred(self):
        return self.dict._get_total_type_transferred()

    def _get_total_type_by_code(self, code):
        return self.dict._get_total_type_by_code(code)

    def _get_surchange_discount_data(self):
        return self.dict._get_surchange_discount_data()

    def _get_advance_values(self):
        return self.dict._get_advance_values()

    def _get_total_advance(self):
        return self.dict._get_total_advance()

    def _get_total_format(self, amount):
        return formatLang(self.env, amount, currency_obj=self.dict.currency_id)
